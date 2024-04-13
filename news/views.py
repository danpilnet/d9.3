from datetime import datetime
from django.views.generic import ListView, DetailView, CreateView, DeleteView, UpdateView
from.models import Post, Category, Subscribe
from .filters import PostFilter
from. forms import PostForm
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.views import View
from django.shortcuts import redirect, render





class PostList(ListView):
    model = Post
    ordering = '-add_time'
    template_name = 'news.html'
    context_object_name = 'news'
    paginate_by = 10
    queryset = Post.objects.filter(pole_ar_ne='NE')


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['time_now'] = datetime.utcnow()
        context['next_sale'] = None
        return context


class PostDetail(DetailView):
    model = Post
    template_name = 'new.html'
    context_object_name = 'new'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['time_now'] = datetime.utcnow()
        context['next_sale'] = None
        return context


class PostSearch(ListView):
    model = Post
    template_name = 'news_search.html'
    context_object_name = 'search'


    def get_queryset(self):
        queryset = super().get_queryset()
        self.filterset = PostFilter(self.request.GET, queryset)
        return self.filterset.qs


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filterset'] = self.filterset
        context['time_now'] = datetime.now()
        return context


class PostCreate(PermissionRequiredMixin, CreateView, LoginRequiredMixin):
    form_class = PostForm
    model = Post
    template_name = 'news_create.html'
    context_object_name = 'create'
    success_url = '/news/'
    permission_required = 'news.add_post'


    def form_valid(self, form):
        post = form.save(commit=False)
        if self.request.path =='/news/create/':
            post.pole_ar_ne = 'NE'
        post.save()

        sub = Subscribe.objects.all()
        for i in sub:
            if i.category_sb == form.cleaned_data['category'][0]:
                html_content = render_to_string('message.html', context={'zagolovok': form.cleaned_data['zagolovok'],
                                                                         'text': form.cleaned_data['text'],
                                                                         'pk': Post.objects.latest('id').id})
                message = EmailMultiAlternatives(subject='Новый пост', from_email='danpilnet@yandex.ru', to=[i.user.email])
                message.attach_alternative(html_content, 'text/html')
                message.send()

        return super().form_valid(form)






class PostEdit(PermissionRequiredMixin,UpdateView, LoginRequiredMixin):
    form_class = PostForm
    model = Post
    template_name = 'news_edit.html'
    context_object_name = 'edit'
    success_url = '/news/'
    permission_required = 'news.change_post'

class PostDelete(DeleteView):
    model = Post
    template_name = 'news_delete.html'
    context_object_name = 'delete'
    success_url = '/news/'



class GetSub(LoginRequiredMixin, View):
    def get(self,request,*args,**kwargs):
        return render(request,'subscribe.html', {'categories':Category.objects.all()})


    def post(self,request,*args,**kwargs):
        save_table = Subscribe(user_id=request.user.pk, category_sb_id=request.POST.get('category'))
        save_table.save()
        return redirect('subscribe')
