from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from .forms import PostForm
from .models import Group, Post, User
from .utils import paginate_page


def index(request):
    """Главная страница."""
    template = "posts/index.html"
    posts = Post.objects.select_related("group", "author")
    page_obj = paginate_page(request, posts)
    context = {"page_obj": page_obj}
    return render(request, template, context)


def group_posts(request, slug):
    """Страница постов одной группы."""
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.select_related("author", "group")
    page_obj = paginate_page(request, posts)
    context = {"page_obj": page_obj, "group": group}
    return render(request, "posts/group_list.html", context)


@login_required
def post_create(request):
    """Страница создания поста"""

    # Можно лучше:
    # Во вьюхе new_post инициализируем форму через request.POST or None
    form = PostForm(request.POST or None)
    if not request.method == "POST":
        return render(request, "posts/new_post.html", {"form": form})

    if not form.is_valid():
        return render(request, "posts/new_post.html", {"form": form})

    post = form.save(commit=False)
    post.author = request.user
    post.save()
    return redirect("posts:profile", request.user)


# Студенты чаще всего делают вот так:
# def new_post(request):
#     if request.method == 'POST':
#         form = PostForm(request.POST)
#         if form.is_valid():
#             post = form.save(commit=False)
#             post.author = user
#             post.save()
#             return redirect('index')
#         return render(request, 'new_post.html', {'form': form})
#     form = PostForm()
#     return render(request, 'new_post.html', {'form': form})

# Или вот так
# def new_post(request):
#     form = PostForm()
#     if request.method == 'POST':
#         form = PostForm(request.POST)
#         if form.is_valid():
#             post = form.save(commit=False)
#             post.author = request.user
#             post.save()
#             return redirect('index')
#     return render(request, 'new_post.html', {'form': form})
#
# Эти варианты тоже приемлемы


def profile(request, username):
    """Страница всех постов автора."""
    user = get_object_or_404(User, username=username)
    page_obj = paginate_page(request, user.posts.select_related("group", "author"))
    template = "posts/profile.html"
    context = {
        "author": user,
        "page_obj": page_obj,
    }
    return render(request, template, context)


def post_detail(request, post_id):
    """Страница детального просмотра поста."""
    post = get_object_or_404(Post, id=post_id)
    template = "posts/post_detail.html"
    context = {
        "post": post,
    }
    return render(request, template, context)


@login_required
def post_edit(request, post_id):
    """Страница редактирования поста."""
    template = "posts/new_post.html"
    post = get_object_or_404(Post, id=post_id)

    if post_id and request.user != post.author:
        return redirect("posts:profile", post_id=post_id)
    form = PostForm(request.POST or None, instance=post)

    if form.is_valid():
        form.save()
        return redirect("posts:post_detail", post_id)

    context = {
        "form": form,
        "post": post,
        "is_edit": True,
    }
    return render(request, template, context)
