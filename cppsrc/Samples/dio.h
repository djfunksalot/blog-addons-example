#include <napi.h>

namespace dio {

    std::string hello();
    Napi::String HelloWrapped(const Napi::CallbackInfo& info);

    int add(int a, int b);
    Napi::Number AddWrapped(const Napi::CallbackInfo& info);

    int channel(int a, int b);
    Napi::Number ChannelWrapped(const Napi::CallbackInfo& info);

    Napi::Object Init(Napi::Env env, Napi::Object exports);
    
}
