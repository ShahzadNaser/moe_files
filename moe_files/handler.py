
# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# MIT License. See license.txt

from __future__ import unicode_literals

import frappe
import frappe.utils
from frappe.utils import cint, get_files_path
from frappe import _, is_whitelisted
import os
from six import text_type

ALLOWED_MIMETYPES = ('image/png', 'image/jpeg', 'application/pdf', 'application/msword',
			'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
			'application/vnd.ms-excel', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
			'application/vnd.oasis.opendocument.text', 'application/vnd.oasis.opendocument.spreadsheet')


@frappe.whitelist(allow_guest=True)
def upload_file():
	user = None
	if frappe.session.user == 'Guest':
		if frappe.get_system_settings('allow_guests_to_upload_files'):
			ignore_permissions = True
		else:
			return
	else:
		user = frappe.get_doc("User", frappe.session.user)
		ignore_permissions = False

	files = frappe.request.files
	is_private = 1
	doctype = frappe.form_dict.doctype
	docname = frappe.form_dict.docname
	fieldname = frappe.form_dict.fieldname
	file_url = frappe.form_dict.file_url
	folder = frappe.form_dict.folder or 'Home'
	method = frappe.form_dict.method
	content = None
	filename = None

	if 'file' in files:
		file = files['file']
		content = file.stream.read()
		filename = file.filename

	frappe.local.uploaded_file = content
	frappe.local.uploaded_filename = filename

	if frappe.session.user == 'Guest' or (user and not user.has_desk_access()):
		import mimetypes
		filetype = mimetypes.guess_type(filename)[0]
		if filetype not in ALLOWED_MIMETYPES:
			frappe.throw(_("You can only upload JPG, PNG, PDF, or Microsoft documents."))

	if method:
		method = frappe.get_attr(method)
		is_whitelisted(method)
		return method()
	else:
		ret = frappe.get_doc({
			"doctype": "File",
			"attached_to_doctype": doctype,
			"attached_to_name": docname,
			"attached_to_field": fieldname,
			"folder": folder,
			"file_name": filename,
			"file_url": file_url,
			"is_private": cint(is_private),
			"content": content
		})
		ret.save(ignore_permissions=ignore_permissions)
		return ret

def before_save_file(doc, method):
    doc.is_private = 1

def before_write_file(file_size):
    from frappe.core.doctype.file.file import File
    File.write_file = write_file

def write_file(self):
	"""write file to disk with a random name (to compare)"""
	self.is_private = 1
	file_path = get_files_path(is_private=self.is_private)

	if os.path.sep in self.file_name:
		frappe.throw(_('File name cannot have {0}').format(os.path.sep))

	# create directory (if not exists)
	frappe.create_folder(file_path)
	# write the file
	self.content = self.get_content()
	if isinstance(self.content, text_type):
		self.content = self.content.encode()

	with open(os.path.join(file_path.encode('utf-8'), self.file_name.encode('utf-8')), 'wb+') as f:
		f.write(self.content)

	return get_files_path(self.file_name, is_private=self.is_private)
