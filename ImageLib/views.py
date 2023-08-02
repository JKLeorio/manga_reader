from django.shortcuts import render, reverse
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from django.views.generic import CreateView, ListView, UpdateView, DetailView, DeleteView, FormView
from django.http import HttpResponseNotFound

from .forms import MangaForm, ChapterForm, VolumeForm
from .models import Manga, Chapter, Volume, Page

# Create your views here.



class MangaCreateView(CreateView, LoginRequiredMixin):
	template_name = 'manga_create.html'
	form_class = MangaForm
	success_url = reverse_lazy('manga_list')


class MangaListView(ListView):
	template_name = 'manga_list.html'
	model = Manga
	context_object_name = 'manga_objects'



class MangaDetailView(DetailView):
	model = Manga
	template_name = "manga_detail.html"
	context_object_name = "manga_object"



class MangaUpdateView(LoginRequiredMixin, UpdateView):
	model = Manga
	form_class = MangaForm
	template_name = "manga_update.html"

	def get_success_url(self):
		pk = self.kwargs["pk"]
		return reverse("manga_update", kwargs = {"pk" : pk})


class MangaDeleteView(LoginRequiredMixin, DeleteView):
	model = Manga
	success_url = reverse_lazy("manga_list")


# class VolumeListView(ListView):
# 	model = Volume
# 	template_name = "Volume_list.html"
# 	context_object_name = "volume_objects"

class VolumeCreateView(CreateView, LoginRequiredMixin):
	template_name = "volume_create.html"
	form_class = VolumeForm
	success_url = reverse_lazy("chapter_create")


class ChapterDetailView(View):

	template_name = "chapter_detail.html"


	def get(self, request, chapter=None, m_pk=None, volume=None, page=None):

		manga_object = Manga.objects.filter(id=m_pk).first()
		if not manga_object:
			return HttpResponseNotFound()
		volume_object = Volume.objects.filter(number=volume, manga=manga_object).first()
		if not manga_object:
			return HttpResponseNotFound()
		chapter_object = Chapter.objects.filter(number=chapter, volume=volume_object).first()
		if not volume_object:
			return HttpResponseNotFound()
		page_objects = Page.objects.filter(chapter=chapter_object)
		if not page_objects:
			return HttpResponseNotFound()
		page_object = page_objects.filter(number=page).first()
		if not page_object:
			return HttpResponseNotFound()
		return render(request, self.template_name, 
			{
			"manga_object":manga_object,
			"volume_object":volume_object,
			"chapter_object":chapter_object,
			"page_objects":page_objects,
			"page_object":page_object
			})

# class ChapterCreateView(FormView, LoginRequiredMixin):

# 	template_name = "chapter_create.html"
# 	form_class = ChapterForm

# 	# def get(self, request):
# 	# 	form = ChapterForm()
# 	# 	return render(request, self.template_name, {"form" : form})

# 	def get_success_url(self):
# 		pk = self.kwargs["pk"]
# 		return reverse("manga_update", kwargs = {"pk" : pk})

# 	def post(self, request):
# 		form_class = self.get_form_class()
# 		form = self.get_form(form_class)
# 		if form.is_valid():
# 			return self.form_valid(form)
# 		else:
# 			return self.form_invalid(form)

# 	def form_valid(self, form):
# 		images = form.cleaned_data["images"]
# 		for image in images:
# 			pass
# 		return super().form_valid()


class ChapterCreateView(View, LoginRequiredMixin):

	template_name = "chapter_create.html"
	form_class = ChapterForm

	def get(self, request):
		form = ChapterForm()
		return render(request, self.template_name, {"form" : form})

	# def post(self, request):
        # form = ChapterForm(request.POST)
        # form2 = ChapterImageForm(request.POST, request.FILES)
        # images = request.FILES.getlist('images')
        # if form.is_valid() and form2.is_valid():
        #     for image in images:
        #     	pass
        #     return redirect(reverse(self.success_url))
	    # context = {'form': form, 'form2': form2}
	    # return render(request, 'projects/project_form.html', context)

	def post(self, request):
		pass
