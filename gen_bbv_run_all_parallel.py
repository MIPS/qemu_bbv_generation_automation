import os
import argparse
import sys
import subprocess


benchmark_input_dict = {
    "gcc" : ["166", "200", "cp-decl", "c-tycheck", "expr2.in", "expr.in", "g23", "s04", "scilab"],
    "astar" : ["BigLakes2048", "rivers"],
    "bzip" : ["chicken", "input.combined","input.program", "input.source", "liberty", "text.html" ],
    "mcf" : ["input"],
    "libquantum" : ["input"],
    "gobmk" : ["13X13", "nngs", "score2", "trevorc", "trevord"],
    "hmmer" : ["nph3.hmm", "retro"],
    "omnetpp" : ["input"],
    "perlbench" : ["checkspam.pl", "diffmail", "splitmail"],
    "xalancbmk" : ["input"],
    "h264ref" : ["foreman_ref_encoder_baseline", "foreman_ref_encoder_main", "sss_encoder_main" ],
    "sjeng" : ["input"]
}

script_base_dir = os.path.dirname(os.path.abspath(sys.argv[0]))   

def parallel_run_launch():
    print("---------------- Running parallel cmd file --------------")
    cmd = "parallel -v -k --joblog ./gen_bbv_cmd_file.log < ./gen_bbv_cmd_file > gen_bbv_cmd_file.out"
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    print(result)
    print("Check gen_bbv_cmd_file.log gen_bbv_cmd_file.out files for parallel run details")


def run(slice_width, execs_dir, cpu, qemu):
    root_path = os.getcwd()
    parallel_cmd_file = "gen_bbv_cmd_file"
    with open(parallel_cmd_file, "w") as f:
        for bench, inputs in benchmark_input_dict.items():
                bench_dir = os.path.join(root_path, bench)
                os.mkdir(bench_dir)
                for input in inputs:
                    input_dir = os.path.join(bench_dir, input)
                    os.mkdir(input_dir)
                    f.write("python3 %s/gen_bbv.py --benchmark %s --input %s --cpu %s --slice_width %s --execs_dir %s --qemu %s\n" % (script_base_dir, bench, input, cpu, slice_width, execs_dir, qemu))
        
    parallel_run_launch()
                    


if __name__ == "__main__":

    define_parser = argparse.ArgumentParser(description='Generate bbv for all benchmarks - Parallely ')

    required_grp = define_parser.add_argument_group('required arguments')

    optional_group = define_parser.add_argument_group('optional arguments')

    #required_grp.add_argument('--benchmark', required=True, type=str, help='Name of the benchmark')
    required_grp.add_argument('--slice_width', required=True, type=int, help='Width of simpoint slice')
    required_grp.add_argument('--execs_dir', required=True, type=str, help='Executable location - full path')
    #required_grp.add_argument('--input', required=True, type=str, help='Benchmark input, if a benchmark has only one input pass "input" Ex: "g23" for gcc, "input" for mcf(single input)')
    required_grp.add_argument('--cpu', required=True, type=str, help='CPU Model - i8500 or kingv')
    optional_group.add_argument('--qemu', type=str, default='/projects/mipssw/toolchains/riscv-linux-gnu/v1.06/bin/qemu-riscv64', help='qemu-riscv location - if nothing specified - default = /projects/mipssw/toolchains/riscv-linux-gnu/v1.06/bin/qemu-riscv64'  )

    args = define_parser.parse_args()

    #benchmark = args.benchmark
    slice_width = args.slice_width
    execs_dir = args.execs_dir
    #input = args.input
    cpu = args.cpu
    qemu = args.qemu

    run(slice_width, execs_dir, cpu, qemu)