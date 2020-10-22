# Copyright (C) 2018 Intel Corporation
#
# SPDX-License-Identifier: MIT
import rules
from rest_framework.permissions import BasePermission, IsAuthenticated, SAFE_METHODS

from . import AUTH_ROLE
from .auth_basic import create_user
from engine.choices import OrderChoices


def register_signals():
    from django.db.models.signals import post_migrate, post_save
    from django.contrib.auth.models import User, Group

    def create_groups(sender, **kwargs):
        for role in AUTH_ROLE:
            db_group, _ = Group.objects.get_or_create(name=role)
            db_group.save()

    post_migrate.connect(create_groups, weak=False)
    post_save.connect(create_user, sender=User)


# AUTH PREDICATES
has_admin_role = rules.is_group_member(str(AUTH_ROLE.ADMIN))
has_accountant_role = rules.is_group_member(str(AUTH_ROLE.ACCOUNTANT))
has_cashier_role = rules.is_group_member(str(AUTH_ROLE.CASHIER))
has_assistant_role = rules.is_group_member(str(AUTH_ROLE.ASSISTANT))

# AUTH PERMISSIONS RULES
rules.add_perm('engine.role.admin', has_admin_role)
rules.add_perm('engine.role.accountant', has_accountant_role)
rules.add_perm('engine.role.cashier', has_cashier_role)
rules.add_perm('engine.role.assistant', has_assistant_role)

rules.add_perm('engine.order.access', has_admin_role | has_cashier_role | has_accountant_role | has_assistant_role)
rules.add_perm('engine.order.create', has_admin_role | has_cashier_role)
rules.add_perm('engine.order.update', has_admin_role | has_cashier_role | has_accountant_role | has_assistant_role)
rules.add_perm('engine.order.delete', has_admin_role)


class AdminRolePermission(BasePermission):
    def has_permission(self, request, view):
        return request.user.has_perm("engine.role.admin")


class AccountantRolePermission(BasePermission):
    def has_permission(self, request, view):
        return request.user.has_perm("engine.role.accountant")


class CashierRolePermission(BasePermission):
    def has_permission(self, request, view):
        return request.user.has_perm("engine.role.cashier")


class AssistantRolePermission(BasePermission):
    def has_permission(self, request, view):
        return request.user.has_perm("engine.role.assistant")


class OrderAccessPermission(BasePermission):
    def has_permission(self, request, view):
        return request.user.has_perm("engine.order.access")

    def has_object_permission(self, request, view, obj):
        if has_admin_role(request.user) or has_accountant_role(request.user) or has_cashier_role(request.user):
            return True
        if obj.status == OrderChoices.ACTIVE:
            return has_assistant_role(request.user)
        return False


class OrderCreatePermission(BasePermission):
    def has_permission(self, request, view):
        return request.user.has_perm("engine.order.create")


class OrderUpdatePermission(BasePermission):
    def has_permission(self, request, view):
        return request.user.has_perm("engine.order.update")

    def has_object_permission(self, request, view, obj):
        if view.action == 'complete':
            return has_assistant_role(request.user)
        elif view.action == 'pay':
            return has_cashier_role(request.user)
        return False


class OrderDeletePermission(BasePermission):
    def has_permission(self, request, view):
        return request.user.has_perm("engine.order.delete")


class OrderGetQuerySetMixin(object):
    def get_queryset(self):
        """
            Method returns a filtered queryset for list request depending on the user's role

            return: queryset
        """
        queryset = super().get_queryset()
        user = self.request.user
        if has_admin_role(user) or has_accountant_role(user) or has_cashier_role(user) or self.detail:
            return queryset
        elif has_assistant_role(user):
            return queryset.filter(status=OrderChoices.ACTIVE)


class OrderPermissions(IsAuthenticated):
    def has_permission(self, request, view):
        """
            Method checks the permissions for the OrderViewSet depending on the request method
            return: boolean
        """
        http_method = request.method
        permissions = [super()]
        if http_method in SAFE_METHODS:
            permissions.append(OrderAccessPermission())
        elif http_method in "POST":
            permissions.append(OrderCreatePermission())
        elif http_method in ["PATCH", 'PUT']:
            permissions.append(OrderUpdatePermission())
        elif http_method == "DELETE":
            permissions.append(OrderDeletePermission())
        else:
            permissions.append(OrderDeletePermission())
        return all([perm.has_permission(request, view) for perm in permissions])
