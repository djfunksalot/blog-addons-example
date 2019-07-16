#include <napi.h>
#include "Samples/dio.h"

Napi::Object InitAll(Napi::Env env, Napi::Object exports) {
  dio::Init(env, exports);
  return exports;
}

NODE_API_MODULE(NODE_GYP_MODULE_NAME, InitAll)
