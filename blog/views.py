from django.shortcuts import render, get_object_or_404, redirect
from .models import Post
from .forms import PostForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required


def index(request):
    posts = Post.objects.all().order_by('-id')
    return render(request, 'blog/index.html', context={
        'posts': posts
    })


@login_required
def post_create(request):
    if request.method == 'POST':
        form = PostForm(request.POST or None, request.FILES or None)

        if form.is_valid():
            form.instance.user = request.user
            form.save()
            messages.success(request, '新規投稿が完了しました')
            return redirect('blog:index')
    else:
        form = PostForm()
    return render(request, 'blog/post_form.html', context={
        'form':form,
    })


def post_detail(request,pk):
    post_data = get_object_or_404(Post, pk=pk)
    return render(request, 'blog/post_detail.html', context={
        'post_data': post_data,
    })


@login_required
def post_edit(request, pk):
    post_data = get_object_or_404(Post, pk=pk)

    if request.method == 'POST':
        form = PostForm(request.POST or None, request.FILES or None, instance=post_data)

        if form.is_valid():
            form.instance.user = request.user
            form.save()
            messages.success(request, '投稿内容を更新しました')
            return redirect('blog:index')

    else:
        form = PostForm(request.POST or None, instance=post_data)

    return render(request, 'blog/post_form.html', context={
        'form': form,
    })


@login_required
def post_delete(request, pk):
    post_data = get_object_or_404(Post, pk=pk)

    post_data.delete()
    messages.error(request, "投稿を削除しました")
    return redirect('blog:index')
