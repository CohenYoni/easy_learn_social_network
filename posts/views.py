from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .models import Post, Comments
from django.views.generic import ListView, DetailView
from .forms import NewPost, Comment, OTHER_CATEGORY
from users.models import Profile, UserCourses
from django.contrib.auth.models import User


# def home_posts(request):
#     other_posts = Post.objects.filter(category="other")
#     user = Profile.objects.get(user=request.user)
#     context = {
#         'posts': Post.objects.all(), 'study_posts': Post.objects.filter(category="other")
#     }
#     return render(request, 'posts/Feed.html', context)


class PostListView(ListView):
    model = Post
    template_name = 'posts/Feed.html'  # <app>/<model>_<viewtype>.html
    context_object_name = 'posts'
    ordering = ['-date']
    paginate_by = 5

    def get_queryset(self):
        profile_obj = Profile.objects.get(user=self.request.user)
        friends_list = tuple(friend.user.username for friend in profile_obj.friends.all())
        all_posts = Post.objects.all()
        user_courses = tuple(course.course_id.course_name for course in UserCourses.objects.filter(user_id=profile_obj))
        posts_to_show = []
        for post in all_posts:
            if post.category == OTHER_CATEGORY and post.author.username in (friends_list + (self.request.user.username,)):
                posts_to_show.append(post)
            elif post.category in user_courses:
                posts_to_show.append(post)
        return posts_to_show


class PostDetailView(DetailView):
    model = Post
    template_name = 'posts/post_detail.html'
    context_object_name = 'post'

    def get_context_data(self, **kwargs):
        context = super(PostDetailView, self).get_context_data(**kwargs)
        # context['comments'] = self.object.comment_set.all()
        context['comments'] = Comments.objects.filter(postId_id=self.object).order_by('-publish_date')
        return context


@login_required
def create_new_post(request):
    if request.method == 'POST':
        form = NewPost(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect('posts:feed')
    form = NewPost
    return render(request, 'posts/new_post.html', {"form": form})