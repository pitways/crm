from wtforms import Form, StringField, validators


class SearchForm(Form):
    search_query = StringField('Search', [validators.DataRequired()])
