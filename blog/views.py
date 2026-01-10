from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Post
from .forms import PostForm
from django.db.models import Q

def home(request):
    posts = Post.objects.all().order_by('-created_at')
    return render(request, 'blog/home.html', {'posts': posts})

@login_required
def post_create(request):
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect('home')
    else:
        form = PostForm()
    return render(request, 'blog/post_form.html', {'form': form})

@login_required
def post_edit(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if request.user != post.author:
        return redirect('home') # Simple permission check
        
    if request.method == 'POST':
        form = PostForm(request.POST, instance=post)
        if form.is_valid():
            form.save()
            return redirect('post_detail', pk=post.pk)
    else:
        form = PostForm(instance=post)
    return render(request, 'blog/post_form.html', {'form': form})

def post_detail(request, pk):
    post = get_object_or_404(Post, pk=pk)
    return render(request, 'blog/post_detail.html', {'post': post})

def search(request):
    query = request.GET.get('q')
    if query:
        posts = Post.objects.filter(
            Q(title__icontains=query) | Q(content__icontains=query)
        )
    else:
        posts = Post.objects.none()
    return render(request, 'blog/home.html', {'posts': posts, 'query': query})