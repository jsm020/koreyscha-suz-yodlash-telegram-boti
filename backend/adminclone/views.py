# adminclone/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.urls import reverse

from botadmin.models import (
    Category, Word, Attempt,
    KnownWord, RepeatSession, RepeatResult
)
from .forms import (
    CategoryForm, WordForm, AttemptForm,
    KnownWordForm, RepeatSessionForm, RepeatResultForm
)

# ------------------------------------------------------------------
# 1. Bitta umumiy lug‘at: model + unga mos forma klasi
#    Pastki chiziqli ham, g‘ijg‘ichli ham kalitlar qo‘shildi
# ------------------------------------------------------------------
MODEL_MAP = {
    # Category
    'categories':      (Category, CategoryForm),

    # Word
    'words':           (Word, WordForm),

    # Attempt
    'attempts':        (Attempt, AttemptForm),

    # KnownWord
    'known_words':     (KnownWord, KnownWordForm),
    'known-words':     (KnownWord, KnownWordForm),

    # RepeatSession
    'repeat_sessions': (RepeatSession, RepeatSessionForm),
    'repeat-sessions': (RepeatSession, RepeatSessionForm),

    # RepeatResult
    'repeat_results':  (RepeatResult, RepeatResultForm),
    'repeat-results':  (RepeatResult, RepeatResultForm),
}

# ------------------------------------------------------------------
# 2. Auth – login / logout
# ------------------------------------------------------------------
def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('adminclone:index')
        messages.error(request, 'Login yoki parol xato.')
    return render(request, 'adminclone/login.html')


@login_required
def logout_view(request):
    logout(request)
    return redirect('adminclone:login')

# ------------------------------------------------------------------
# 3. Dashboard
# ------------------------------------------------------------------
@login_required
def index(request):
    """
    Asosiy sahifa – hamma modellar ro‘yxati.
    Faqat bir marta ko‘ringan nomlarni chiqarish uchun set() ishlatildi.
    """
    unique_models = {}
    for key, (model, _) in MODEL_MAP.items():
        # 'repeat-sessions' va 'repeat_sessions' ikkita kalit,
        # ammo ular bitta modelga tegishli; dublikatlarni olib tashlaymiz
        if model not in unique_models.values():
            unique_models[key] = model

    return render(request, 'adminclone/index.html', {'models': unique_models})

# ------------------------------------------------------------------
# 4. Model ro‘yxati
# ------------------------------------------------------------------
# --- adminclone/views.py ---
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q          # Q() orqali qidiruv
from django.db.models import Q, Field, CharField, TextField, IntegerField, BigIntegerField, AutoField
...

TEXT_TYPES  = (CharField, TextField)
NUM_TYPES   = (IntegerField, BigIntegerField, AutoField)

def get_search_fields(model):
    """
    Modeldan qidiruvga yaroqli ustunlar ro‘yxatini qaytaradi.
    Char/Text → icontains, Integer → to‘g‘ri tenglik.
    """
    fields = []
    for f in model._meta.get_fields():
        # ManyToOne / ForeignKey dan voz kechamiz, faqat oddiy ustunlar
        if f.is_relation:
            continue
        if isinstance(f, TEXT_TYPES):
            fields.append(f"{f.name}__icontains")
        elif isinstance(f, NUM_TYPES):
            fields.append(f"{f.name}")
    return fields or ['pk']      # hech bo‘lmasa pk bo‘lsin

def apply_search(queryset, search_fields, keyword):
    """
    Berilgan queryset ga Q() so‘rovi qo‘shadi.
    """
    if not keyword:
        return queryset
    q = Q()
    for field in search_fields:
        # Sonlar bo‘yicha matn qidirib holi yo‘q – har ikkalasini tekshirib qo‘yamiz
        if field.endswith('__icontains'):
            q |= Q(**{field: keyword})
        else:  # integer/PK
            if keyword.isdigit():
                q |= Q(**{field: int(keyword)})
    return queryset.filter(q)

# ------------------------------------------------------------------
# 3. CRUD view’lar orasida faqat model_list o‘zgardi
# ------------------------------------------------------------------
@login_required
def model_list(request, model_name):
    model, _ = MODEL_MAP.get(model_name, (None, None))
    if model is None:
        return render(request, 'adminclone/index.html',
                      {'error': 'Noto‘g‘ri model tanlandi.'})

    # ---------------- Qidiruv ----------------
    keyword       = request.GET.get('q', '').strip()
    search_fields = get_search_fields(model)
    objects_qs    = apply_search(model.objects.all(), search_fields, keyword)

    # ---------------- Pagination ------------
    paginator   = Paginator(objects_qs, 10)          # 10 ta element per sahifa
    page_number = request.GET.get('page', 1)
    try:
        page_obj = paginator.page(page_number)
    except (PageNotAnInteger, EmptyPage):
        page_obj = paginator.page(1)

    # Jadval ustunlari
    fields = model._meta.get_fields()
    return render(
        request,
        'adminclone/model_list.html',
        {
            'model_name':         model_name,
            'model_verbose_name': model._meta.verbose_name_plural,
            'fields':             fields,
            'page_obj':           page_obj,
            'query':              keyword,
        }
    )


# ------------------------------------------------------------------
# 5. Create
# ------------------------------------------------------------------
@login_required
def model_create(request, model_name):
    model, form_class = MODEL_MAP.get(model_name, (None, None))
    if model is None:
        return render(request, 'adminclone/index.html',
                      {'error': 'Noto‘g‘ri model tanlandi.'})

    if request.method == 'POST':
        form = form_class(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, f'{model._meta.verbose_name} yaratildi.')
            return redirect('adminclone:model_list', model_name=model_name)
    else:
        form = form_class()

    return render(request, 'adminclone/model_form.html', {
        'form':       form,
        'model_name': model_name,
        'action':     'Create',
    })

# ------------------------------------------------------------------
# 6. Update
# ------------------------------------------------------------------
@login_required
def model_update(request, model_name, pk):
    model, form_class = MODEL_MAP.get(model_name, (None, None))
    if model is None:
        return render(request, 'adminclone/index.html',
                      {'error': 'Noto‘g‘ri model tanlandi.'})

    obj = get_object_or_404(model, pk=pk)
    if request.method == 'POST':
        form = form_class(request.POST, request.FILES, instance=obj)
        if form.is_valid():
            form.save()
            messages.success(request, f'{model._meta.verbose_name} yangilandi.')
            return redirect('adminclone:model_list', model_name=model_name)
    else:
        form = form_class(instance=obj)

    return render(request, 'adminclone/model_form.html', {
        'form':       form,
        'model_name': model_name,
        'action':     'Update',
    })

# ------------------------------------------------------------------
# 7. Delete
# ------------------------------------------------------------------
@login_required
def model_delete(request, model_name, pk):
    model, _ = MODEL_MAP.get(model_name, (None, None))
    if model is None:
        return render(request, 'adminclone/index.html',
                      {'error': 'Noto‘g‘ri model tanlandi.'})

    obj = get_object_or_404(model, pk=pk)
    if request.method == 'POST':
        obj.delete()
        messages.success(request, f'{model._meta.verbose_name} o‘chirildi.')
        return redirect('adminclone:model_list', model_name=model_name)

    return render(request, 'adminclone/model_delete.html', {
        'object':     obj,
        'model_name': model_name,
    })
