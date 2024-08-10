import sys
import os
import argparse
import subprocess

# to use
# python gen_bbv.py --benchmark bzip --input chicken --cpu i8500 --slice_width 100000000 --execs_dir /mips/proj/specmemdump/full_spec_slices/20240629 


def get_elf_name(cpu):
    return{
        "astar": "astar_base." + cpu,
        "bwaves": "bwaves_base." + cpu,
        "bzip": "bzip2_base." + cpu,
        "cactusADM": "cactusADM_base." + cpu,
        "calculix": "calculix_base." + cpu,
        "gcc": "gcc_base." + cpu,
        "GemsFDTD": "GemsFDTD_base." + cpu,
        "gobmk": "gobmk_base." + cpu,
        "gromacs": "gromacs_base." + cpu,
        "h264ref": "h264ref_base." + cpu,
        "hmmer": "hmmer_base." + cpu,
        "lbm": "lbm_base." + cpu,
        "leslie3d": "leslie3d_base." + cpu,
        "libquantum": "libquantum_base." + cpu,
        "mcf": "mcf_base." + cpu,
        "milc": "milc_base." + cpu,
        "omnetpp": "omnetpp_base." + cpu,
        "perlbench": "perlbench_base." + cpu,
        "povray": "povray_base." + cpu,
        "sjeng": "sjeng_base." + cpu,
        "soplex": "soplex_base." + cpu,
        "tonto": "tonto_base." + cpu,
        "wrf": "wrf_base." + cpu,
        "xalancbmk": "Xalan_base." + cpu,
        "zeusmp": "zeusmp_base." + cpu
    }

def run(benchmark, slice_width, execs_dir, input, cpu, qemu, root_path):

    exe_map = get_elf_name(cpu)

    if not os.path.isdir("/mips/proj/specmemdump/full_spec_slices/input_files/%s" % (benchmark)):
        print("Benchmark arguments to be passed to qemu unknown, look at SPEC documentation to get the arguments for the benchmark")
        sys.exit(1)

    bench_dir = os.path.join(root_path, benchmark)
    input_dir = os.path.join(bench_dir, input)
    # Qemu should run here, benchmarks like astar, href need some files in the directory to run 
    qemu_run_dir = "/mips/proj/specmemdump/full_spec_slices/input_files/%s/ref/" % (benchmark)

    if not os.path.isdir(input_dir):
        os.makedirs(input_dir)
    os.chdir(qemu_run_dir)


    bbv_file = "%s/%s_%dm.bbv" % (input_dir, benchmark, slice_width/1000000)
    #exe = "/mips/proj/specmemdump/full_spec_slices/%s/%s" % (execs_dir, exe_map[benchmark])
    exe = "%s/%s" % (execs_dir, exe_map[benchmark])
    log_file = "%s/%s_%dm.log" % (input_dir,benchmark, slice_width/1000000)

    bench_args_file = "/mips/proj/specmemdump/full_spec_slices/input_files/%s/ref/%s.incmd" % (benchmark, input)
    with open(bench_args_file, 'r') as f:
        bench_args = f.read().split("\n")[0]

    ### Change this to take compiler version too
    ### Use the toolchain qemu
    #qemu_cmd = "/projects/mipssw/toolchains/riscv-linux-gnu/%s/bin/qemu-riscv64 -bbvout %s -bbv-interval %d %s %s" % ("v1.06", bbv_file, slice_width, exe, bench_args)
    #qemu_cmd = "/projects/mipssw/toolchains/riscv-elf/v2.02/qemu8-centos8/bin/qemu-riscv64 -bbvout %s -bbv-interval %d -plugin /home/sstephens.scratch/runsimpoint/qemu/libinsn.so -d plugin %s  %s" % ( bbv_file, slice_width, exe, bench_args)
    #qemu_cmd = "/projects/mipssw/toolchains/riscv-elf/v2.02/qemu8-centos8/bin/qemu-riscv64 -cpu rv64 -bbvout %s -bbv-interval %d --plugin /projects/mipssw/toolchains/riscv-linux-gnu/v2.02/qemu8-centos8/plugins/libinsn.so -d plugin %s %s" % ( bbv_file, slice_width, exe, bench_args)
    qemu_cmd = "%s -bbvout %s -bbv-interval %d %s %s" % (qemu, bbv_file, slice_width, exe, bench_args)
    
    cur_time = os.popen('date +%T').read().split("\n")[0]
    with open(log_file, 'w') as f:
        f.write("(%s) Executing: %s\n" % (cur_time, qemu_cmd) )
    
    print("------------------ Running qemu - bbv, inst count gen -----------------")
    result = subprocess.run(qemu_cmd, shell=True, capture_output=True, text=True)
    print(result)
    cur_time = os.popen('date +%T').read().split("\n")[0]
    with open(log_file, 'a') as f:
        f.write("(%s) Finished generating bbv file: %s\n" % (cur_time, bbv_file))


if __name__ == "__main__":

    define_parser = argparse.ArgumentParser(description='Generate bbv for a single ')

    required_grp = define_parser.add_argument_group('required arguments')

    optional_group = define_parser.add_argument_group('optional arguments')

    required_grp.add_argument('--benchmark', required=True, type=str, help='Name of the benchmark')
    required_grp.add_argument('--slice_width', required=True, type=int, help='Width of simpoint slice')
    required_grp.add_argument('--execs_dir', required=True, type=str, help='Executable location - full path')
    required_grp.add_argument('--input', required=True, type=str, help='Benchmark input, if a benchmark has only one input pass "input" Ex: "g23" for gcc, "input" for mcf(single input)')
    required_grp.add_argument('--cpu', required=True, type=str, help='CPU Model - i8500 or kingv')
    optional_group.add_argument('--qemu', type=str, default='/projects/mipssw/toolchains/riscv-linux-gnu/v1.06/bin/qemu-riscv64', help='qemu-riscv location - if nothing specified - default = /projects/mipssw/toolchains/riscv-linux-gnu/v1.06/bin/qemu-riscv64'  )

    args = define_parser.parse_args()
    root_path = os.getcwd()

    benchmark = args.benchmark
    slice_width = args.slice_width
    execs_dir = args.execs_dir
    input = args.input
    cpu = args.cpu
    qemu = args.qemu

    run(benchmark, slice_width, execs_dir, input, cpu, qemu, root_path)
