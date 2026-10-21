#pragma once
#include <cerrno>
#include <chrono>
#include <cstring>
#include <stdexcept>
#include <string>
#include <thread>
#include <vector>
#include <fcntl.h>
#include <unistd.h>
#include <sys/stat.h>

namespace hp {
inline bool FileExists(const std::string& path) {struct stat s;return ::stat(path.c_str(),&s)==0;}
class TailReader {
 public:
  TailReader(const char* path,const char* done):path_(path),done_(done),buffer_(1<<20) {
    while(!FileExists(path_)) {
      if(FileExists(done_))throw std::runtime_error("trace absent after encoder exits");
      std::this_thread::sleep_for(std::chrono::milliseconds(50));
    }
    fd_=::open(path,O_RDONLY);if(fd_<0)throw std::runtime_error("cannot open trace");
  }
  ~TailReader(){if(fd_>=0)::close(fd_);}
  bool Read(void* dst,size_t n) {
    char* out=static_cast<char*>(dst);
    while(n) {
      if(pos_==length_&&!Refill())return false;
      size_t count=std::min(n,length_-pos_);std::memcpy(out,buffer_.data()+pos_,count);
      pos_+=count;out+=count;n-=count;consumed_+=count;
    }
    return true;
  }
  uint64_t Consumed()const{return consumed_;}
 private:
  bool Refill() {
    for(;;) {
      ssize_t n=::read(fd_,buffer_.data(),buffer_.size());
      if(n>0){pos_=0;length_=size_t(n);return true;}
      if(n<0&&errno==EINTR)continue;
      if(n<0)throw std::runtime_error("trace read failed");
      if(FileExists(done_)) {
        n=::read(fd_,buffer_.data(),buffer_.size());
        if(n>0){pos_=0;length_=size_t(n);return true;}
        if(n<0)throw std::runtime_error("trace final read failed");
        return false;
      }
      std::this_thread::sleep_for(std::chrono::milliseconds(5));
    }
  }
  std::string path_,done_;std::vector<char> buffer_;int fd_=-1;
  size_t pos_=0,length_=0;uint64_t consumed_=0;
};
}
