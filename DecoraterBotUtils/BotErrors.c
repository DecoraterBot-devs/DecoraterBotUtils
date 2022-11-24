/*
 * Bot Errors defined and Used For DecoraterBot.
 */
#include <Python.h>

static struct PyModuleDef BotErrorsmodule = {
  PyModuleDef_HEAD_INIT, "BotErrors", NULL, -1, NULL
};

PyMODINIT_FUNC
PyInit_BotErrors(void) {
  PyObject *m;
  m = PyModule_Create(&BotErrorsmodule);
  if (m == NULL)
    return NULL;
  PyObject* concurrent_futures = PyImport_ImportModule("concurrent.futures");
  PyObject* concurrent_futuresDict = PyModule_GetDict(concurrent_futures);
  PyObject* TimeoutErrorClass = PyDict_GetItemString(concurrent_futuresDict, "TimeoutError");
  PyModule_AddObject(m, "CommandTimeoutError", TimeoutErrorClass);
  return m;
}
