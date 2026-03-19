from flask import flash
def flash_form_errors(form):
    for errors in form.errors.values():
        for err_msg in errors:
            flash(err_msg, "danger")