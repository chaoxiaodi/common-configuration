<!--
 * @Author: guangcai.liu
 * @Date: 2023-10-12 11:52:24
 * @LastEditors: guangcai.liu
 * @LastEditTime: 2023-11-15 12:14:43
 * @FilePath: /common-configuration/system-kernel/optimization.md
-->
# 关闭 selinux
查看selinux 状态

getenforce

临时关闭

setenforce 0

配置文件永久关闭

    # This file controls the state of SELinux on the system.
    # SELINUX= can take one of these three values:
    #     enforcing - SELinux security policy is enforced.
    #     permissive - SELinux prints warnings instead of enforcing.
    #     disabled - No SELinux policy is loaded.
    # See also:
    # https://docs.fedoraproject.org/en-US/quick-docs/getting-started-with-selinux/#getting-started-with-selinux-selinux-states-and-modes
    #
    # NOTE: In earlier Fedora kernel builds, SELINUX=disabled would also
    # fully disable SELinux during boot. If you need a system with SELinux
    # fully disabled instead of SELinux running with no policy loaded, you
    # need to pass selinux=0 to the kernel command line. You can use grubby
    # to persistently set the bootloader to boot with selinux=0:
    #
    #    grubby --update-kernel ALL --args selinux=0
    #
    # To revert back to SELinux enabled:
    #
    #    grubby --update-kernel ALL --remove-args selinux
    #
    SELINUX=disabled
    # SELINUXTYPE= can take one of these three values:
    #     targeted - Targeted processes are protected,
    #     minimum - Modification of targeted policy. Only selected processes are protected.
    #     mls - Multi Level Security protection.
    SELINUXTYPE=targeted

# ulimit

    /etc/security/limits.conf

    root soft nofile 102400
    root hard nofile 102400
    * soft nofile 102400
    * hard nofile 102400

# sysctl

    net.core.somaxconn = 102400
    net.core.netdev_max_backlog = 5000
    net.core.rmem_max = 16777216
    net.core.wmem_max = 16777216
    net.ipv4.tcp_syncookies = 1
    net.ipv4.tcp_wmem = 4096 12582912 16777216
    net.ipv4.tcp_rmem = 4096 12582912 16777216
    net.ipv4.tcp_max_syn_backlog = 8192
    net.ipv4.tcp_slow_start_after_idle = 0
    net.ipv4.tcp_tw_reuse = 1
    net.ipv4.tcp_tw_recycle = 1
    net.ipv4.tcp_fin_timeout = 10
    net.ipv4.tcp_keepalive_time = 600
    net.ipv4.tcp_keepalive_intvl = 2
    net.ipv4.tcp_keepalive_probes = 2
    net.ipv4.ip_local_port_range = 10240 65535

    fs.protected_hardlinks = 1
    fs.protected_symlinks = 1


