# 安装
1. 依次安装好msys2、cmake、make、open ocd、arm gcc、git bash

2. 打开新的终端，输入查看是否安装成功
   ~~~bash
   cmake --version
   make --version
   openocd --version
   arm-none-eabi-gcc --version
   ~~~

3. 在vscode中使用快捷键`ctrl + ~`打开底部命令窗选择使用`git bash`打开终端

<img src="E:\Code\install\doc\asset\image.png" alt="image" style="zoom:25%;" />

4. 运行如下命令，即可编译并下载

```bash
cd example/
./run.sh
```

# 常见问题

1. 编译成功但是无法下载。出现如下提示，则为下载器检测不到，请检查链接是否稳定

```bash
$ ./run.sh 
Project root directory name: example
正在运行CMake配置...
CMake Warning (dev) at CMakeLists.txt:31 (enable_language):
  project() should be called prior to this enable_language() call.   
This warning is for project developers.  Use -Wno-dev to suppress it.

Build type: Debug
-- Configuring done (0.1s)
-- Generating done (0.1s)
-- Build files have been written to: /e/Code/install/example/build
正在编译项目...
[100%] Built target example
编译成功完成
Using target: example
ELF file: /e/Code/install/example/build/example.elf
/usr/bin/objcopy: Unable to recognise the architecture of the input file `/e/Code/install/example/build/example.elf'
Conversion to BIN and HEX completed
Open On-Chip Debugger 0.12.0
Licensed under GNU GPL v2
For bug reports, read
        http://openocd.org/doc/doxygen/bugs.html
Info : auto-selecting first available session transport "swd". To override use 'transport select <transport>'.
Error: unable to find a matching CMSIS-DAP device
** OpenOCD init failed **
shutdown command invoked
```

