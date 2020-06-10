from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.views.decorators.cache import cache_page
from .models import Post, Group, User, Follow
from .forms import PostForm, CommentForm


@cache_page(20)
def index(request):
    post_list = Post.objects.all()
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(
        request,
        'index.html',
        {'page': page, 'paginator': paginator}
    )


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = group.group_posts.all()
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(
        request,
        'group.html',
        {'group': group, 'page': page, 'paginator': paginator}
    )


@login_required
def new_post(request):
    if request.method == 'POST':
        form = PostForm(request.POST or None, files=request.FILES or None)
        if form.is_valid():
            new_article = form.save(commit=False)
            new_article.author = request.user
            new_article.save()
            return redirect('index')
        return render(request, 'new_post.html', {'form': form})
    form = PostForm()
    return render(request, 'new_post.html', {'form': form})


def profile_view(request, username):
    profile = get_object_or_404(User, username=username)
    articles = profile.author_posts.all()
    if request.user.is_authenticated:
        user_follower_author = request.user.follower.filter(
            author__username=username
        ).exists()
    else:
        user_follower_author = False
    paginator = Paginator(articles, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    context = {
        'user_follower_author': user_follower_author,
        'profile': profile,
        'page': page,
        'paginator': paginator,
    }
    return render(request, 'profile_view.html', context)


def post_view(request, username, post_id):
    profile = get_object_or_404(User, username=username)
    article = get_object_or_404(profile.author_posts, id=post_id)
    if request.user.is_authenticated:
        user_follower_author = request.user.follower.filter(
            author__username=username
        ).exists()
    else:
        user_follower_author = False
    comments = article.comments.all()
    comment_form = CommentForm()
    context = {
        'profile': profile,
        'article': article,
        'user_follower_author': user_follower_author,
        'comments': comments,
        'form': comment_form
    }
    return render(request, 'post_view.html', context)


def post_edit(request, username, post_id):
    profile = get_object_or_404(User, username=username)
    if request.user != profile:
        return redirect('post_view', username=username, post_id=post_id)
    article = get_object_or_404(profile.author_posts, id=post_id)

    if request.method == 'POST':
        form = PostForm(
            request.POST or None,
            files=request.FILES or None,
            instance=article
        )
        if form.is_valid():
            edited_article = form.save()
            edited_article.save()
            return redirect('post_view', username=username, post_id=post_id)
        return render(request, 'new_post.html', {'form': form})

    form = PostForm(instance=article)
    return render(
        request,
        'new_post.html',
        {'form': form, 'article': article}
    )


def page_not_found(request, exception):
    return render(request, 'misc/404.html', {'path': request.path}, status=404)


def server_error(request):
    return render(request, 'misc/500.html', status=500)


@login_required
def add_comment(request, username, post_id):
    profile = get_object_or_404(User, username=username)
    article = get_object_or_404(profile.author_posts, id=post_id)
    # список комментов к посту
    comments = article.comments.all()
    new_comment = None
    if request.method == 'POST':
        comment_form = CommentForm(
            request.POST or None,
            files=request.FILES or None
        )
        if comment_form.is_valid():
            new_comment = comment_form.save(commit=False)
            new_comment.author = request.user
            new_comment.post_id = article.id
            new_comment.save()
            return redirect('post_view', username=username, post_id=post_id)
        return render(
            request,
            'post_view.html',
            {'form': comment_form}
        )
    else:
        comment_form = CommentForm()
    context = {
        'profile': profile,
        'article': article,
        'comments': comments,
        'new_comment': new_comment,
        'form': comment_form
    }
    return render(request, 'post_view.html', context)


@login_required
def follow_index(request):
    profile = get_object_or_404(User, username=request.user)
    my_follower_queryset = profile.follower.values_list('author', flat=True)
    articles = Post.objects.filter(author__in=my_follower_queryset)
    paginator = Paginator(articles, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    context = {
        'my_follower_queryset': my_follower_queryset,
        'profile': profile,
        'page': page,
        'paginator': paginator,
    }
    return render(request, 'follow.html', context)


@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    if request.user != author:
        Follow.objects.get_or_create(user=request.user, author=author)
    return redirect('follow_index')


@login_required
def profile_unfollow(request, username):
    request.user.follower.filter(author__username=username).delete()
    return redirect('follow_index')


# на кого подписан
def follower_view(request, username):
    profile = get_object_or_404(User, username=username)
    follower_queryset = profile.follower.values_list('author', flat=True)
    authors = User.objects.filter(id__in=follower_queryset)
    context = {
        'profile': profile,
        'authors': authors,
    }
    return render(request, 'list_view.html', context)


# кто подписан
def following_view(request, username):
    profile = get_object_or_404(User, username=username)
    follower_queryset = profile.following.values_list('user', flat=True)
    authors = User.objects.filter(id__in=follower_queryset)
    context = {
        'profile': profile,
        'authors': authors,
    }
    return render(request, 'list_view.html', context)
