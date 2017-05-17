/*
Bot Errors defined and Used For DecoraterBot.
*/
#include <Python.h>

static struct PyModuleDef BotErrorsmodule = {
  PyModuleDef_HEAD_INIT, "BotErrors", NULL, -1, NULL
};

PyMODINIT_FUNC
PyInit_BotErrors(void) {
  PyObject *m;
  static PyObject *MaxPlayersError;
  static PyObject *CogUnloadError;
  m = PyModule_Create(&BotErrorsmodule);
  if (m == NULL)
    return NULL;
  MaxPlayersError = PyErr_NewExceptionWithDoc("BotErrors.MaxPlayersError", "Exception thrown when the user tries to add more players than the maximum number set.", NULL, NULL);
  CogUnloadError = PyErr_NewExceptionWithDoc("BotErrors.CogUnloadError", "Raised when an error occurs when unloading a cog.", NULL, NULL);
  PyObject* concurrent_futures = PyImport_ImportModule("concurrent.futures");
  PyObject* concurrent_futuresDict = PyModule_GetDict(concurrent_futures);
  PyObject* TimeoutErrorClass = PyDict_GetItemString(concurrent_futuresDict, "TimeoutError");
  Py_INCREF(MaxPlayersError);
  Py_INCREF(CogUnloadError);
  PyModule_AddObject(m, "MaxPlayersError", MaxPlayersError);
  PyModule_AddObject(m, "CogUnloadError", CogUnloadError);
  PyModule_AddObject(m, "CommandTimeoutError", TimeoutErrorClass);
  return m;
}
