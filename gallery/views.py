from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView
from .models import Foto, Album

# Create your views here.

class GalleryView(ListView):
    def get_queryset(self):
        """Return the last five published questions."""
        unique_saisons = []
        unique_photographers = []
        albums = []



def gallery(request):
    alben = Album.objects.all()
    return render(request, 'gallery.html', {'alben': alben})


def album(request, pk):
    album = get_object_or_404(Album, id=pk)
    fotos = Foto.objects.filter(album_ref=album)

    return render(request, "album.html",
                  {"album": album,
                   "fotos": fotos})


def foto(request, album_id, foto_id):
    album = get_object_or_404(Album, id=album_id)
    fotos = Foto.objects.filter(album_ref=album)
    foto = get_object_or_404(Foto, id=foto_id)

    return render(request, "foto.html",
                  {"album": album,
                   "fotos": fotos,
                   "foto": foto})
