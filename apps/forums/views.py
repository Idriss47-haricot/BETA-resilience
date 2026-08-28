from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic import ListView, DetailView
from django.http import JsonResponse

from .forms import SujetForm, MessageForm
from .models import ForumCategorie, ForumSujet, ForumMessage


def api_nouvelles_reponses(request, sujet_id):
    """
    API JSON pour récupérer les nouveaux messages en temps réel.
    """
    last_reponse_id = request.GET.get('last_id', 0)
    
    nouvelles_reponses = ForumMessage.objects.filter(
        sujet_id=sujet_id,
        id__gt=last_reponse_id
    ).order_by('date_creation')

    data = []
    for rep in nouvelles_reponses:
        data.append({
            'id': rep.id,
            'auteur': rep.auteur.username,
            'contenu': rep.contenu,
            'date': rep.date_creation.strftime('%d/%m/%Y à %H:%M')
        })

    return JsonResponse({'reponses': data})


class ForumIndexView(ListView):
    model = ForumCategorie
    template_name = 'forums/index.html'
    context_object_name = 'categories'
    
    def get_queryset(self):
        return ForumCategorie.objects.filter(est_active=True).order_by('ordre')


@login_required
def creer_sujet(request, slug):
    """
    Créer un nouveau sujet dans une catégorie
    """
    categorie = get_object_or_404(ForumCategorie, slug=slug)
    
    if request.method == 'POST':
        form = SujetForm(request.POST)
        if form.is_valid():
            sujet = form.save(commit=False)
            sujet.categorie = categorie
            sujet.auteur = request.user
            sujet.save()
            messages.success(request, '✅ Votre sujet a été créé avec succès !')
            return redirect('forums:sujet_detail', slug=sujet.slug)
    else:
        form = SujetForm()
    
    return render(request, 'forums/creer_sujet.html', {
        'form': form,
        'categorie': categorie
    })


class SujetDetailView(DetailView):
    model = ForumSujet
    template_name = 'forums/sujet_detail.html'
    context_object_name = 'sujet'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        self.object.incrementer_vues()
        context['messages'] = self.object.messages.all()
        context['form'] = MessageForm()
        return context


@login_required
def repondre_sujet(request, slug):
    sujet = get_object_or_404(ForumSujet, slug=slug)
    
    if sujet.est_ferme:
        messages.warning(request, 'Ce sujet est fermé.')
        return redirect('forums:sujet_detail', slug=sujet.slug)
    
    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.sujet = sujet
            message.auteur = request.user
            message.save()
            messages.success(request, '✅ Votre réponse a été ajoutée !')
            return redirect('forums:sujet_detail', slug=sujet.slug)
    
    return redirect('forums:sujet_detail', slug=sujet.slug)


class CategorieDetailView(ListView):
    """
    Détail d'une catégorie avec ses sujets
    """
    model = ForumSujet
    template_name = 'forums/categorie_detail.html'
    context_object_name = 'sujets'
    paginate_by = 20
    
    def get_queryset(self):
        self.categorie = get_object_or_404(ForumCategorie, slug=self.kwargs['slug'])
        return ForumSujet.objects.filter(categorie=self.categorie).order_by(
            '-est_epingle', '-date_creation'
        )
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categorie'] = self.categorie
        return context
