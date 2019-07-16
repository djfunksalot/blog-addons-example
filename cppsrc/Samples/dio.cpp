#include "dio.h"

std::string dio::hello(){
    return "Hello World";
}

int dio::add(int a, int b){
  return a + b;
}

Napi::String dio::HelloWrapped(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    Napi::String returnValue = Napi::String::New(env, dio::hello());
    return returnValue;
}


Napi::Number dio::AddWrapped(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    if (info.Length() < 2 || !info[0].IsNumber() || !info[1].IsNumber()) {
        Napi::TypeError::New(env, "Number expected").ThrowAsJavaScriptException();
    } 

    Napi::Number first = info[0].As<Napi::Number>();
    Napi::Number second = info[1].As<Napi::Number>();

    int returnValue = dio::add(first.Int32Value(), second.Int32Value());
    
    return Napi::Number::New(env, returnValue);
}

Napi::Object dio::Init(Napi::Env env, Napi::Object exports) {
    exports.Set("hello", Napi::Function::New(env, dio::HelloWrapped));
    exports.Set("add", Napi::Function::New(env, dio::AddWrapped));
    return exports;
}
