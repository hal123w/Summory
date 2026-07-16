from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, LogoutView
from django.db.models import Count
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views.generic import CreateView

from .forms import SignUpForm, SummaryCreateForm, SummaryEditForm
from .models import Summary
from .services import SummarizationError, summarize_text


class SignUpView(CreateView):
    form_class = SignUpForm
    template_name = 'registration/signup.html'
    success_url = reverse_lazy('summaries:login')


class SummoryLoginView(LoginView):
    template_name = 'registration/login.html'


class SummoryLogoutView(LogoutView):
    next_page = reverse_lazy('summaries:login')


def _user_categories(user):
    return (
        Summary.objects.filter(user=user)
        .exclude(category='')
        .values('category')
        .annotate(count=Count('id'))
        .order_by('category')
    )


def _base_context(user, active_category=None):
    return {
        'categories': _user_categories(user),
        'active_category': active_category,
        'nav': 'list',
    }


@login_required
def summary_list(request):
    category = (request.GET.get('category') or '').strip()
    qs = Summary.objects.filter(user=request.user)
    if category:
        qs = qs.filter(category=category)

    context = _base_context(request.user, active_category=category or None)
    context['summaries'] = qs
    context['filter_category'] = category
    return render(request, 'summaries/list.html', context)


@login_required
def summary_create(request):
    suggestions = (
        Summary.objects.filter(user=request.user)
        .exclude(category='')
        .values_list('category', flat=True)
        .distinct()
        .order_by('category')
    )

    if request.method == 'POST':
        form = SummaryCreateForm(request.POST)
        if form.is_valid():
            try:
                summary_body = summarize_text(form.cleaned_data['original_text'])
            except SummarizationError as exc:
                messages.error(request, str(exc))
            else:
                obj = form.save(commit=False)
                obj.user = request.user
                obj.category = (obj.category or '').strip()
                obj.summary_text = summary_body
                if not (obj.title or '').strip():
                    obj.title = summary_body.strip().splitlines()[0][:80]
                obj.save()
                messages.success(request, '要約を保存しました。')
                return redirect('summaries:detail', pk=obj.pk)
    else:
        form = SummaryCreateForm()

    context = _base_context(request.user)
    context.update({
        'form': form,
        'category_suggestions': suggestions,
        'nav': 'create',
    })
    return render(request, 'summaries/create.html', context)


@login_required
def summary_detail(request, pk):
    obj = get_object_or_404(Summary, pk=pk, user=request.user)
    context = _base_context(request.user, active_category=obj.category or None)
    context['summary'] = obj
    return render(request, 'summaries/detail.html', context)


@login_required
def summary_edit(request, pk):
    obj = get_object_or_404(Summary, pk=pk, user=request.user)
    suggestions = (
        Summary.objects.filter(user=request.user)
        .exclude(category='')
        .values_list('category', flat=True)
        .distinct()
        .order_by('category')
    )

    if request.method == 'POST':
        form = SummaryEditForm(request.POST, instance=obj)
        if form.is_valid():
            edited = form.save(commit=False)
            edited.category = (edited.category or '').strip()
            edited.save()
            messages.success(request, '保存しました。')
            return redirect('summaries:detail', pk=obj.pk)
    else:
        form = SummaryEditForm(instance=obj)

    context = _base_context(request.user)
    context.update({
        'form': form,
        'summary': obj,
        'category_suggestions': suggestions,
    })
    return render(request, 'summaries/edit.html', context)


@login_required
def summary_delete(request, pk):
    obj = get_object_or_404(Summary, pk=pk, user=request.user)
    if request.method == 'POST':
        obj.delete()
        messages.success(request, '削除しました。')
        return redirect('summaries:list')

    context = _base_context(request.user)
    context['summary'] = obj
    return render(request, 'summaries/confirm_delete.html', context)
