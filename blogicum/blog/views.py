import datetime as dt
from typing import Any, Dict

from django.core.exceptions import PermissionDenied
from django.db.models.query import QuerySet
from django.db.models import Count
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse_lazy, reverse
from django.utils import timezone
from django.views.generic import (
    ListView,
    CreateView,
    UpdateView,
    DeleteView,
    DetailView,
)
from django.contrib.auth.mixins import LoginRequiredMixin
from blog.models import Post, Category, Comment
from blog.models import User
from blog.forms import PostForm, CommentForm


class PostMixin:
    model = Post
    paginate_by = 10


class CommentMixin:
    model = Comment
    form_class = CommentForm

    def get_object(self, queryset=None):
        return get_object_or_404(
            Comment, pk=self.kwargs["comment_pk"],
            post_id=self.kwargs["post_pk"]
        )

    def dispatch(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.author != request.user:
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse_lazy("blog:post_detail",
                            kwargs={"pk": self.kwargs["post_pk"]})


class PostListView(PostMixin, ListView):
    def get_queryset(self):
        posts = Post.objects.prefetch_related(
            "author", "category", "location"
        ).filter(
            pub_date__lt=dt.datetime.now(),
            is_published=True,
            category__is_published=True,
        ).annotate(
            comment_count=Count("comment")
        ).order_by("-pub_date")
        return posts

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        return context


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self) -> str:
        return reverse("blog:profile", kwargs={
            "username": self.request.user.username})


class PostDetailView(DetailView):
    model = Post

    def dispatch(self, request, *args, **kwargs):
        instance = self.get_object()
        if (instance.author != request.user and not instance.is_published
                or (instance.author != request.user and instance.category
                    and not instance.category.is_published)
                or (instance.author != request.user
                    and instance.pub_date > timezone.now())):
            return render(request, 'pages/404.html', status=404)
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["form"] = CommentForm()
        context["comments"] = self.object.comment.select_related("author")
        return context


class PostUpdateView(LoginRequiredMixin, UpdateView):
    model = Post
    form_class = PostForm

    def dispatch(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.author != request.user:
            return HttpResponseRedirect(reverse('blog:post_detail',
                                                kwargs={'pk': instance.pk}))
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


class PostDeleteView(LoginRequiredMixin, DeleteView):
    model = Post
    form_class = PostForm
    template_name = "blog/post_form.html"
    success_url = reverse_lazy("blog:post_list")

    def dispatch(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.author != request.user:
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)


class CommentCreateView(LoginRequiredMixin, CreateView):
    post_object = None
    model = Comment
    form_class = CommentForm

    def dispatch(self, request, *args, **kwargs):
        self.post_object = get_object_or_404(Post, pk=kwargs["pk"])
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.post = self.post_object
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("blog:post_detail", kwargs={"pk": self.post_object.pk})


class CommentUpdateView(CommentMixin, LoginRequiredMixin, UpdateView):
    pass


class CommentDeleteView(CommentMixin, LoginRequiredMixin, DeleteView):
    template_name = "blog/comment_form.html"


class CategoryListView(PostMixin, ListView):
    template_name = "blog/category.html"
    context_object_name = "page_obj"

    def dispatch(self, request, *args, **kwargs):
        self.category = get_object_or_404(Category,
                                          slug=self.kwargs['category_slug'],
                                          is_published=True)
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self) -> QuerySet[Any]:
        self.category = get_object_or_404(Category,
                                          slug=self.kwargs["category_slug"],
                                          is_published=True)
        return (
            Post.objects.filter(category=self.category,
                                pub_date__lt=dt.datetime.now(),
                                category__is_published=True,
                                is_published=True,
                                )
            .annotate(comment_count=Count("comment"))
            .order_by("-pub_date")
            .all()
        )

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["category"] = self.category
        return context


class ProfileView(PostMixin, ListView):
    template_name = "blog/profile.html"
    context_object_name = "page_obj"
    ordering = "-pub_date"

    def get_queryset(self):
        self.author = get_object_or_404(User, username=self.kwargs['username'])
        return (
            Post.objects.prefetch_related("author", "category", "location")
            .filter(
                author=self.author,
            )
            .annotate(comment_count=Count("comment"))
            .order_by("-pub_date")
            .all()
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["profile"] = self.author
        return context


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    template_name = "blog/profile_update.html"
    fields = [
        "username",
        "first_name",
        "last_name",
        "email",
    ]

    def dispatch(self, request, *args, **kwargs):
        self.object = get_object_or_404(User, username=self.kwargs["username"])
        return super().dispatch(request, *args, **kwargs)

    def get_object(self, queryset=None):
        return get_object_or_404(User, username=self.kwargs["username"])

    def get_success_url(self):
        return reverse("blog:profile",
                       kwargs={"username": self.object.username})
