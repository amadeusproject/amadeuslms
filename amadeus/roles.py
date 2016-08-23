from rolepermissions.roles import AbstractUserRole

class Student(AbstractUserRole):
	available_permissions = {
		'view_courses': True,
		'view_modules': True,
		'view_categories': True,
		'subscribe_course': True,
	}

class Professor(AbstractUserRole):
	available_permissions = {
		'create_courses_record': True,
		'edit_courses_record': True,
		'delete_courses': True,
		'view_modules': True,
		'create_modules': True,
		'edit_modules': True,
		'delete_modules': True,
		'view_categories': True,
		'create_categories': True,
		'edit_categories': True,
		'delete_categories': True,
	}

class SystemAdmin(AbstractUserRole):
	pass