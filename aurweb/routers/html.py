""" AURWeb's primary routing module. Define all routes via @app.app.{get,post}
decorators in some way; more complex routes should be defined in their
own modules and imported here. """
from http import HTTPStatus

from fastapi import APIRouter, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse

import aurweb.config

from aurweb.templates import make_context, render_template

router = APIRouter()


@router.get("/favicon.ico")
async def favicon(request: Request):
    """ Some browsers attempt to find a website's favicon via root uri at
    /favicon.ico, so provide a redirection here to our static icon. """
    return RedirectResponse("/static/images/favicon.ico")


@router.post("/language", response_class=RedirectResponse)
async def language(request: Request,
                   set_lang: str = Form(...),
                   next: str = Form(...),
                   q: str = Form(default=None)):
    """
    A POST route used to set a session's language.

    Return a 303 See Other redirect to {next}?next={next}. If we are
    setting the language on any page, we want to preserve query
    parameters across the redirect.
    """
    from aurweb.db import session

    if next[0] != '/':
        return HTMLResponse(b"Invalid 'next' parameter.", status_code=400)

    query_string = "?" + q if q else str()

    # If the user is authenticated, update the user's LangPreference.
    if request.user.is_authenticated():
        request.user.LangPreference = set_lang
        session.commit()

    # In any case, set the response's AURLANG cookie that never expires.
    response = RedirectResponse(url=f"{next}{query_string}",
                                status_code=int(HTTPStatus.SEE_OTHER))
    secure_cookies = aurweb.config.getboolean("options", "disable_http_login")
    response.set_cookie("AURLANG", set_lang,
                        secure=secure_cookies, httponly=True)
    return response


@router.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """ Homepage route. """
    context = make_context(request, "Home")
    return render_template(request, "index.html", context)


# A route that returns a error 503. For testing purposes.
@router.get("/raisefivethree", response_class=HTMLResponse)
async def raise_service_unavailable(request: Request):
    raise HTTPException(status_code=503)
