"""
    Routes
    ~~~~~~
"""
# For PDF Conversion
import os

import pypandoc

# For PDF Conversion
from flask import send_file

from flask import Blueprint
from flask import flash
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for
from flask_login import current_user
from flask_login import login_required
from flask_login import login_user
from flask_login import logout_user
from datetime import datetime

from wiki.core import Processor
from wiki.web.forms import EditorForm
from wiki.web.forms import LoginForm
from wiki.web.forms import SearchForm
from wiki.web.forms import URLForm
from wiki.web import current_wiki
from wiki.web import current_users
from wiki.web.user import protect
from wiki.web.last_edited import *

bp = Blueprint('wiki', __name__)


@bp.route('/')
@protect
def home():
    read_timestamps()
    last_edited = get_timestamp('home')
    page = current_wiki.get('home')
    if page:
        return display('home')
    return render_template('home.html', last_edited=last_edited)


@bp.route('/index/')
@protect
def index():
    pages = current_wiki.index()
    return render_template('index.html', pages=pages)


@bp.route('/<path:url>/')
@protect
def display(url):
    page = current_wiki.get_or_404(url)
    last_edited = get_timestamp(url)
    return render_template('page.html', page=page, last_edited=last_edited)


@bp.route('/create/', methods=['GET', 'POST'])
@protect
def create():
    form = URLForm()
    if form.validate_on_submit():
        return redirect(url_for(
            'wiki.edit', url=form.clean_url(form.url.data)))
    return render_template('create.html', form=form)


"""

revisions() requires only

from datetime import datetime

will render a page with a list of revisions from content/revisions/url

"""


@bp.route('/revisions/<path:url>/', methods=['GET', 'POST'])
@protect
def revisions(url):
    pages = current_wiki.revisions(url)
    return render_template('revisions.html', pages=pages)


@bp.route('/edit/<path:url>/', methods=['GET', 'POST'])
@protect
def edit(url):
    page = current_wiki.get(url)
    form = EditorForm(obj=page)
    if form.validate_on_submit():
        if not page:
            page = current_wiki.get_bare(url)
        form.populate_obj(page)
        page.save()
        flash('"%s" was saved.' % page.title, 'success')
        update_timestamp(url)
        return redirect(url_for('wiki.display', url=url))
    return render_template('editor.html', form=form, page=page, date=datetime.now().strftime("%c"))


@bp.route('/preview/', methods=['POST'])
@protect
def preview():
    data = {}
    processor = Processor(request.form['body'])
    data['html'], data['body'], data['meta'] = processor.process()
    return data['html']


@bp.route('/move/<path:url>/', methods=['GET', 'POST'])
@protect
def move(url):
    page = current_wiki.get_or_404(url)
    form = URLForm(obj=page)
    if form.validate_on_submit():
        newurl = form.url.data
        remove_timestamp(url)
        update_timestamp(newurl)
        current_wiki.move(url, newurl)
        return redirect(url_for('wiki.display', url=newurl))
    return render_template('move.html', form=form, page=page)


@bp.route('/delete/<path:url>/')
@protect
def delete(url):
    page = current_wiki.get_or_404(url)
    current_wiki.delete(url)
    remove_timestamp(url)
    flash('Page "%s" was deleted.' % page.title, 'success')
    return redirect(url_for('wiki.home'))


"""
In order for pdf() to function, the following imports need to be made:
    import pypandoc
    from flask import send_file
    
pdf(url) allows for the creation of PDF documents by converting the markdown content files. Conversion is aided by
pypandoc. Once converted, flask.send_file() returns the PDF file to the user.

PDF support can also be found in page.html, which allows users to download the page via button click rather than
API. The HTML tag simply directs to the pdf(url) defined below.

    PARAMETERS:
        url - the wiki page's url (e.g. 'home').
    VARIABLES:
        result_dir - A directory to store generated PDFs
        source_markdown_file - Markdown file that the user wants to convert to PDF
        output_file - PDF file sent to the user
    RETURNS:
        A PDF File

"""


@bp.route('/pdf/<path:url>', methods=['GET'])
@protect
def pdf(url):
    # Variable declarations.
    # I'm assuming content/pdfs work instead and be better?
    # result_dir = 'C:/Users/Beans/wiki/content/pdfs'
    result_dir = os.path.join(os.getcwd(), 'content/pdfs')
    if not os.path.exists(result_dir):
        os.makedirs(result_dir)
    source_markdown_file = 'content/' + url + '.md'
    output_file = result_dir + "/" + url + ".pdf"

    # pypandoc is a wrapper for Pandoc, a conversion service. It works it's magic behind the scenes.
    output = pypandoc.convert_file(source_markdown_file, 'pdf', outputfile=output_file)

    # For PDFs, pypandoc will return a blank string after a successful conversion.
    if output == '':
        return send_file(output_file, attachment_filename=url + '.pdf')
    else:
        # If for some reason the code ends up here (i.e. conversion unsuccessful), it simple returns to home.
        flash('PDF generation failed.', 'failure')
        return redirect('wiki.home')


@bp.route('/tags/')
@protect
def tags():
    tags = current_wiki.get_tags()
    return render_template('tags.html', tags=tags)


@bp.route('/tag/<string:name>/')
@protect
def tag(name):
    tagged = current_wiki.index_by_tag(name)
    return render_template('tag.html', pages=tagged, tag=name)


@bp.route('/search/', methods=['GET', 'POST'])
@protect
def search():
    form = SearchForm()
    if form.validate_on_submit():
        results = current_wiki.search(form.term.data, form.ignore_case.data)
        return render_template('search.html', form=form,
                               results=results, search=form.term.data)
    return render_template('search.html', form=form, search=None)


@bp.route('/user/login/', methods=['GET', 'POST'])
def user_login():
    form = LoginForm()
    if form.validate_on_submit():
        user = current_users.get_user(form.name.data)
        login_user(user)
        user.set('authenticated', True)
        flash('Login successful.', 'success')
        return redirect(request.args.get("next") or url_for('wiki.index'))
    return render_template('login.html', form=form)


@bp.route('/user/logout/')
@login_required
def user_logout():
    current_user.set('authenticated', False)
    logout_user()
    flash('Logout successful.', 'success')
    return redirect(url_for('wiki.index'))


@bp.route('/user/')
def user_index():
    pass


@bp.route('/user/create/')
def user_create():
    pass


@bp.route('/user/<int:user_id>/')
def user_admin(user_id):
    pass


@bp.route('/user/delete/<int:user_id>/')
def user_delete(user_id):
    pass


"""
    Error Handlers
    ~~~~~~~~~~~~~~
"""


@bp.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404

