#!/bin/bash

#解压新版本的openssl
tar -xf '/tmp/upgrade_openssl/openssl-1.0.2k.tar.gz' -C '/usr/local/'
openssl_dir="/usr/local/openssl-1.0.2k"
openssl_rpm="$(ls ${openssl_dir} | grep -E 'openssl(.*?)\.rpm$')"
openssl_rpm_lib="$(ls ${openssl_dir} | grep -E 'openssl-libs-(.*?)\.rpm$')"
cd ${openssl_dir} && yum clean all &&
    for rpm in $openssl_rpm;do
        if [ $rpm != $openssl_rpm_lib ];then
            openssl_rpm_=$rpm
        fi
    done
yum localinstall --disablerepo='*' -y $openssl_rpm_ $openssl_rpm_lib &>/dev/null
#再次查看openssl版本
openssl version

#创建文件作为升级后标志（留痕）
echo 'upgrade openssl success' >> '/tmp/upgrade_openssl/is_upgrade_openssl.txt'
