#include "Python.h"

PyDoc_STRVAR(light__receiver__doc__, "Light receiver");

static PyObject *
py_init(PyObject *self, PyObject *args)
{
	int num_pages=0, page_size=0, ret=0;

	if (!PyArg_ParseTuple(args, "ii", &num_pages, &page_size)) {
		return NULL;
	}
	ret = init(num_pages, page_size);
	return PyInt_FromLong((long) ret);
}

static PyObject *
py_get_num_pages(PyObject *self)
{
	int num_pages=0;

	num_pages = get_num_pages();
	return PyInt_FromLong((long) num_pages);
}

static PyObject *
py_get_page_size(PyObject *self)
{
	int page_size=0;

	page_size = get_page_size();
	return PyInt_FromLong((long) page_size);
}

static PyObject *
py_get_data(PyObject *self, PyObject *args)
{
	int data=0;

	if (!PyArg_ParseTuple(args, "i", &data)) {
		return NULL;
	}

	get_data(&data);

	return Py_BuildValue("i", data);
}

static PyMethodDef light_receiver_methods[] = {
	{"init",  py_init, METH_VARARGS, NULL },
	{"get_num_pages", (PyCFunction)py_get_num_pages, METH_NOARGS, NULL },
	{"get_page_size", (PyCFunction)py_get_page_size, METH_NOARGS, NULL },
	{"get_data", py_get_data, METH_VARARGS, NULL },
	{NULL}
};

PyMODINIT_FUNC
initlight_receiver(void)
{
	Py_InitModule3("light_receiver", light_receiver_methods, light__receiver__doc__);
}

// Python

import light_receiver

print light_receiver.init(103, 10000)
print light_receiver.get_num_pages()
print light_receiver.get_page_size()
print light_receiver.get_data(val)
