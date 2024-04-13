from datetime import datetime
from django.views.generic import ListView, DetailView, CreateView, DeleteView, UpdateView
from news. models import Post, Subscribe, Category
from. forms import PostForm
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
from django.views import View
from django.shortcuts import redirect, render


class ArticlesList(ListView):
    model = Post
    ordering = '-add_time'
    template_name = 'news.html'
    context_object_name = 'news'
    paginate_by = 10
    queryset = Post.objects.filter(pole_ar_ne='AR')


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['time_now'] = datetime.utcnow()
        context['next_sale'] = None
        return context


class ArticlesDetail(DetailView):
    model = Post
    template_name = 'new.html'
    context_object_name = 'new'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['time_now'] = datetime.utcnow()
        context['next_sale'] = None
        return context




class ArticlesCreate(PermissionRequiredMixin, LoginRequiredMixin, CreateView):
    form_class = PostForm
    model = Post
    template_name = 'news_create.html'
    context_object_name = 'create'
    success_url = '/articles/'
    permission_required = 'news.add_post'

    def form_valid(self, form):
        post = form.save(commit=False)
        if self.request.path =='/articles/create/':
            post.pole_ar_ne = 'AR'
        post.save()


        subAR = Subscribe.objects.all()
        for i in subAR:
            if i.category_sb == form.cleaned_data['category'][0]:
                html_content = render_to_string('message.html', context={'zagolovok': form.cleaned_data['zagolovok'],
                                                                         'text': form.cleaned_data['text'],
                                                                         'pk': Post.objects.latest('id').id})
                message = EmailMultiAlternatives(subject='Новая статья', from_email='danpilnet@yandex.ru', to=[i.user.email])
                message.attach_alternative(html_content, 'text/html')
                message.send()

        return super().form_valid(form)


class ArticlesEdit(PermissionRequiredMixin,UpdateView, LoginRequiredMixin):
    form_class = PostForm
    model = Post
    template_name = 'news_edit.html'
    context_object_name = 'edit'
    success_url = '/articles/'
    permission_required = 'news.change_post'

class ArticlesDelete(DeleteView):
    model = Post
    template_name = 'news_delete.html'
    context_object_name = 'delete'
    success_url = '/articles/'



class GetSubAR(LoginRequiredMixin, View):
    def get(self,request,*args,**kwargs):
        return render(request,'subscribe.html', {'categories':Category.objects.all()})


    def post(self,request,*args,**kwargs):
        save_table = Subscribe(user_id=request.user.pk, category_sb_id=request.POST.get('category'))
        save_table.save()
        return redirect('subscribe')