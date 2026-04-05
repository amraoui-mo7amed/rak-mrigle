from functools import wraps
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.core.exceptions import PermissionDenied
from django.http import JsonResponse


def provider_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect(reverse("user_auth:login"))
        if not hasattr(request.user, "profile"):
            raise PermissionDenied
        if request.user.profile.role != "provider":
            raise PermissionDenied
        return view_func(request, *args, **kwargs)

    return _wrapped_view


def user_is_self(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            if request.headers.get("X-Requested-With") == "XMLHttpRequest":
                return JsonResponse(
                    {"success": False, "message": "Authentication required."},
                    status=401,
                )
            return redirect(reverse("user_auth:login"))
        pk = kwargs.get("pk")
        if pk and request.user.pk != pk and not request.user.is_superuser:
            if request.headers.get("X-Requested-With") == "XMLHttpRequest":
                return JsonResponse(
                    {"success": False, "message": "Permission denied."}, status=403
                )
            raise PermissionDenied
        return view_func(request, *args, **kwargs)

    return _wrapped_view


def admin_required(view_func):
    """
    Decorator for views that checks that the user is logged in and is a superuser,
    raising PermissionDenied if not.
    """

    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect(reverse("user_auth:login"))
        if not request.user.is_superuser:
            raise PermissionDenied
        return view_func(request, *args, **kwargs)

    return _wrapped_view


def with_pagination(
    per_page=10, context_name="page_obj", queryset_name="queryset", template="list.html"
):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            response = view_func(request, *args, **kwargs)

            # If response is not a dict (e.g. HttpResponse), skip
            if not isinstance(response, dict):
                return response

            queryset = response.get(queryset_name)
            if queryset is None:
                return response

            page_number = request.GET.get("page", 1)
            paginator = Paginator(queryset, per_page)

            try:
                page_obj = paginator.page(page_number)
            except PageNotAnInteger:
                page_obj = paginator.page(1)
            except EmptyPage:
                page_obj = paginator.page(paginator.num_pages)

            response[context_name] = page_obj
            return render(request, f"{template}.html", response)

        return _wrapped_view

    return decorator
