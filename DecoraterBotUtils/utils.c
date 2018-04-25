/*
Utils for DecoraterBot.
*/
#include <Python.h>

static PyObject *
get_plugin_full_name(PyObject *args)
{
  char *plugin_name;
  if (plugin_name != NULL)
  {
    return PyUnicode_FromString(
      "DecoraterBotCore.plugins." + plugin_name);
  }
  Py_RETURN_NONE;
}

static PyObject *
construct_reply(PyObject *args)
{
  Py_RETURN_NONE;
}

static struct PyModuleDef utilsmodule = {
  PyModuleDef_HEAD_INIT, "utils", NULL, -1, NULL
};

PyMODINIT_FUNC
PyInit_utils(void) {
  PyObject *m;
  m = PyModule_Create(& utilsmodule);
  if (m == NULL)
    return NULL;
  // other code here.
  return m;
}
