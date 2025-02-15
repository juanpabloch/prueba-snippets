from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from django.views import View

from .forms import UserAuthenticationForm, SnippetForm


class Login(View):
    def get(self, request, *args, **kwargs):
        form = UserAuthenticationForm()
        context = {"form": form}
        return render(request, "snippets/login.html", context)

    def post(self, request, *args, **kwargs):
        form = UserAuthenticationForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect("index")
            else:
                form.add_error(None, "Usuario o contraseña incorrectos")
                return render(request, "snippets/login.html", {"form": form})
        else:
            form.add_error(None, "Error al intentar ingresar")
            return render(request, "snippets/login.html", {"form": form})
        

class Logout(View):
    def get(self, request, *args, **kwargs):
        logout(request)
        return redirect("index")


class Index(View):
    def get(self, request, *args, **kwargs):
        # TODO: Fetch and display all public snippets
        return render(request, "index.html", {"snippets": []})


#    TODO: Implement this class to handle snippet creation, only for authenticated users.
class SnippetAdd(View):
    def get(self, request, *args, **kwargs):
        form = SnippetForm()

        context = {
            "action": "Cargar",
            "form": form
        }
        return render(request, "snippets/snippet_add.html", context)


#    TODO: Implement this class to handle snippet editing. Allow editing only for the owner.
class SnippetEdit(View):
    def get(self, request, *args, **kwargs):
        form = SnippetForm()

        context = {
            "action": "Editar",
            "form": form
        }
        return render(request, "snippets/snippet_add.html", context)


#    TODO: Implement this class to handle snippet deletion. Allow deletion only for the owner.
class SnippetDelete(View):
    def get(self, request, *args, **kwargs):
        pass


class SnippetDetails(View):
    def get(self, request, *args, **kwargs):
        snippet_id = self.kwargs["id"]
        # TODO: Implement logic to get snippet by ID
        # snippet = Snippet.objects.get(id=snippet_id)
        # Add conditions for private snippets

        # context = {"snippet": snippet}
        return render(request, "snippets/snippet.html")


class UserSnippets(View):
    def get(self, request, *args, **kwargs):
        username = self.kwargs["username"]
        # TODO: Fetch user snippets based on username and public/private logic
        # snippets = Snippet.objects.filter(...)

        # context = {"snippetUsername": username, "snippets": snippets}
        return render(request, "snippets/user_snippets.html")


class SnippetsByLanguage(View):
    def get(self, request, *args, **kwargs):
        language = self.kwargs["language"]
        # TODO: Fetch snippets based on language
        return render(request, "index.html", {"snippets": []})
