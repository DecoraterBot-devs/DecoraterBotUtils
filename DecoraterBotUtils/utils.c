/*
Utils for DecoraterBot.
*/
#include <Python.h>

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