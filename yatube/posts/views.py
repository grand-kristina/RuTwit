from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.cache import cache_page
from django.http import HttpResponseRedirect

from .forms import CommentForm, PostForm
from .models import Follow, Group, Post, User, Like
import random

from users.forms import UpdateForm


def index(request):
    post_list = Post.objects.select_related('group').filter(is_valid=True)
    paginator = Paginator(post_list, 5)

    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(
        request,
        'index.html',
        {'page': page, 'paginator': paginator}
    )


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.filter(is_valid=True)
    paginator = Paginator(posts, 5)

    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)

    return render(
        request,
        'group.html',
        {'group': group, 'page': page, 'paginator': paginator}
    )


@login_required
def new_post(request):
    if request.method != 'POST':
        form = PostForm()
        return render(
            request, 'new_post.html', {'form': form, 'is_edit': False}
        )

    form = PostForm(request.POST, request.FILES)
    if not form.is_valid():
        return render(
            request, 'new_post.html', {'form': form, 'is_edit': False}
        )

    post = form.save(commit=False)
    post.author = request.user
    post.save()


    return redirect('index')


def profile(request, username):
    user = get_object_or_404(User, username=username)

    posts = user.posts.filter(is_valid=True)
    paginator = Paginator(posts, 10)

    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)

    form = CommentForm()
    is_edit_profile = user == request.user
    
    form_user = UpdateForm()

    time_here = random.randint(5, 55)

    following = request.user.is_authenticated and Follow.objects.filter(
        user=request.user, author=user
    ).exists()
    return render(
        request,
        'profile.html',
        {
            'author': user,
            'page': page,
            'paginator': paginator,
            'form': form,
            'form_user': form_user,
            'is_edit_profile': is_edit_profile,
            'following': following,
            'time_here': time_here
        }
    )


def post_view(request, username, post_id):
    post = get_object_or_404(Post, pk=post_id, is_valid=True, author__username=username)
    posts_count = post.author.posts.filter(is_valid=True).count()
    form = CommentForm()
    return render(
        request,
        'post.html',
        {
            'post': post,
            'author': post.author,
            'posts_count': posts_count,
            'form': form
        }
    )


@login_required
def post_edit(request, username, post_id):
    post = get_object_or_404(Post, pk=post_id, author__username=username)
    if post.author != request.user:
        return redirect('post', username=username, post_id=post_id)

    form = PostForm(request.POST or None,
                    files=request.FILES or None,
                    instance=post)
    if form.is_valid():
        form.save()
        return redirect('post', post_id=post_id, username=username)

    return render(
        request,
        'new_post.html',
        {'post': post, 'form': form, 'is_edit': True}
    )


@login_required
def add_comment(request, username, post_id):
    post = get_object_or_404(Post, pk=post_id, is_valid=True, author__username=username)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('post', post_id=post_id, username=username)


@login_required
def update_user(request, username):
    author = get_object_or_404(User, username=username)
    form = UpdateForm(request.POST, request.FILES, instance=author.profile)
    if form.is_valid():
        form.save()
    return redirect('profile', username=username)


def page_not_found(request, exception):
    return render(request, 'misc/404.html', {'path': request.path}, status=404)


def server_error(request):
    return render(request, 'misc/500.html', status=500)


@login_required
def follow_index(request):
    posts = Post.objects.filter(author__following__user=request.user, is_valid=True)
    paginator = Paginator(posts, 10)

    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)

    return render(
        request,
        'follow.html',
        {
            'page': page,
            'paginator': paginator,
        }
    )


@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    if (
            Follow.objects.filter(author=author, user=request.user).exists()
            or request.user == author
    ):
        return redirect('profile', username=username)
    Follow.objects.create(author=author, user=request.user)

    return redirect('profile', username=username)


@login_required
def profile_unfollow(request, username):
    author = get_object_or_404(User, username=username)
    follow_qs = Follow.objects.filter(author=author, user=request.user)
    if follow_qs.exists():
        follow_qs.delete()

    return redirect('profile', username=username)


@login_required
def post_like(request, post_id):
    url = '/'+'/'.join(request.META.get('HTTP_REFERER').split('/')[3:])
    post = get_object_or_404(Post, pk=post_id, is_valid=True)
    Like.objects.get_or_create(post=post, user=request.user)
    return HttpResponseRedirect(url)


@login_required
def post_unlike(request, post_id):
    url = '/'+'/'.join(request.META.get('HTTP_REFERER').split('/')[3:])
    post = get_object_or_404(Post, pk=post_id, is_valid=True)
    like_qs = Like.objects.filter(post=post, user=request.user)
    print(like_qs)
    if like_qs.exists():
        like_qs.delete()

    return HttpResponseRedirect(url)