from django.contrib import messages
from django.shortcuts import redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import CreateView

from ..forms import AuthorForm, PainterForm
from ..models import Page, Author, Painter


class AuthorCreateView(CreateView, LoginRequiredMixin):
    template_name = "author_create.html"
    model = Author
    form_class = AuthorForm


class PainterCreateView(CreateView, LoginRequiredMixin):
    template_name = "painter_create.html"
    model = Painter
    form_class = PainterForm


def delete_page(request, pk):
    try:
        page = Page.objects.get(id=pk)
    except Page.DoesNotExist:
        messages.success(
            request, 'Object Does not exit'
        )
        return redirect('chapter_create')

    page.delete()
    messages.success(
        request, 'Image deleted successfully'
    )
    return redirect('chapter_update', pk=page.chapter.id)
