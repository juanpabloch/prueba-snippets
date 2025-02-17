from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.cache import cache
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.decorators import method_decorator
from django.views import View

import json
import redis

from .models import Snippet, User, Language
from .forms import UserAuthenticationForm, SnippetForm, UserRegisterForm
from .utils import send_email, get_snippet_format
from django.conf import settings


class Login(View):
    def get(self, request, *args, **kwargs):
        form = UserAuthenticationForm()
        context = {"form": form}
        return render(request, "login.html", context)

    def post(self, request, *args, **kwargs):
        form = UserAuthenticationForm(data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect("index")
            else:
                form.add_error(None, "Usuario o contraseña incorrectos")
                return render(request, "login.html", {"form": form})
        else:
            return render(request, "login.html", {"form": form})
        

class Logout(View):
    def get(self, request, *args, **kwargs):
        logout(request)
        return redirect("index")


class UserRegisterView(View):
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect("index")
        
        return super().dispatch(request, *args, **kwargs)
    
    def get(self, request, *args, **kwargs):
        form = UserRegisterForm()
        context = {"form": form}
        return render(request, "register.html", context)

    def post(self, request, *args, **kwargs):
        form = UserRegisterForm(data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get("username")
            email = form.cleaned_data.get("email")
            password = form.cleaned_data.get("password1")
            
            user = User.objects.create_user(username, email, password)
            print("USER: ", user)
            return redirect("login")
        else:
            print("ERROR: ", form.errors)
            return render(request, "register.html", {"form": form})


class Index(View):
    def get(self, request, *args, **kwargs):
        snippets = Snippet.objects.filter(public=True)

        context = {"snippets": snippets}
        return render(request, "index.html", context)



class SnippetDetails(View):
    def get(self, request, *args, **kwargs):
        snippet_id = self.kwargs["id"]
        snippet = Snippet.objects.filter(id=snippet_id)
        
        if not snippet.exists():
            return redirect("index")

        snippet = snippet.first()

        if request.user != snippet.user and not snippet.public:
            return redirect("index")

        result = get_snippet_format(snippet.snippet, snippet.language.slug)
        
        context = {
            "snippet": snippet,
            "result": result
        }
        return render(request, "snippets/snippet.html", context)



class SnippetAdd(View):
    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)
    
    def get(self, request, *args, **kwargs):
        form = SnippetForm()
        context = {
            "action": "Cargar",
            "form": form
        }
        return render(request, "snippets/snippet_add.html", context)
    
    def post(self, request, *args, **kwargs):
        try:
            form = SnippetForm(data=request.POST)
            if form.is_valid():
                snippet = form.save(commit=False)
                snippet.user = request.user
                snippet.save()

                # Send email
                data = {
                    "snippet_name": snippet.name,
                    "snippet_description": snippet.description,
                    "sent_to": snippet.user.email,
                }
                
                redis_client = redis.from_url(settings.CACHES["default"]["LOCATION"])
                redis_client.rpush("snippets_list", json.dumps(data))
                
                return redirect("user_snippets", username=snippet.user.username)
            else:
                return render(request, "snippets/snippet_add.html", {"form": form})
        except Exception as e:
            print(e)
            return redirect("index")


class SnippetEdit(View):
    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        snippet = get_object_or_404(Snippet, id=self.kwargs["id"])
        if not snippet.user == request.user:
            return redirect("index")

        self.snippet = snippet
        return super().dispatch(request, *args, **kwargs)
    
    def get(self, request, *args, **kwargs):
        form = SnippetForm(instance=self.snippet)
        
        context = {
            "action": "Editar",
            "form": form
        }
        return render(request, "snippets/snippet_add.html", context)

    def post(self, request, *args, **kwargs):
        form = SnippetForm(data=request.POST, instance=self.snippet)
        if form.is_valid():
            snippet = form.save(commit=False)
            snippet.save()

            return redirect("snippet" , id=snippet.id)
        else:
            return render(request, "snippets/snippet_add.html", {"form": form})
        

class SnippetDelete(View):
    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        snippet = get_object_or_404(Snippet, id=self.kwargs["id"])
        if not snippet.user == request.user:
            return redirect("index")

        self.snippet = snippet
        return super().dispatch(request, *args, **kwargs)
    
    def get(self, request, *args, **kwargs):
        try:
            self.snippet.delete()
            if request.GET.get("from") == "user":
                return redirect("user_snippets", username=self.snippet.user.username)
            
            return redirect("index")
        except Exception as e:
            print(e)
            return redirect("index")


class UserSnippets(View):
    def get(self, request, *args, **kwargs):
        username = self.kwargs["username"]
        user = get_object_or_404(User, username=username)

        snippets = Snippet.objects.filter(user=user)
        
        if not request.user == user:
            snippets = snippets.filter(public=True)
        
        context = {
            "snippetUsername": username, 
            "snippets": snippets
        }
        return render(request, "snippets/user_snippets.html", context)


class SnippetsByLanguage(View):
    def get(self, request, *args, **kwargs):
        lang = self.kwargs["language"]
        language = get_object_or_404(Language, slug=lang)
        snippets = Snippet.objects.filter(language=language, public=True)
        context = {
            "snippets": snippets,
            "language_header": language
        }
        return render(request, "index.html", context)
