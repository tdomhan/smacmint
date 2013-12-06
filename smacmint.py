##
# wrapping: A program making it easy to use hyperparameter
# optimization software.
# Copyright (C) 2013 Katharina Eggensperger and Matthias Feurer and Tobias Domhan
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

#! /usr/bin/env python

import optparse
import os
import subprocess
import sys


from google.protobuf import text_format
from spearmint_pb2 import Experiment, PYTHON
from spearmint_pb2 import *


def spearmint_to_smac(filename):
    fh = open(filename, 'rb')
    exp = Experiment()
    text_format.Merge(fh.read(), exp)
    fh.close()

    if exp.language != PYTHON:
        raise NotImplementedError("We only implemented python optimization...")

    fh = open(filename + ".pcs", "w")
    for para in exp.variable:
        name = para.name
        for i in range(para.size):
            indexed_name = name + "@" + str(i)
            if para.type == Experiment.ParameterSpec.INT:
                # A [1, 10] [1]i
                default = int((para.min + para.max) / 2)
                # TODO: round to middle
                fh.write("%s [%d, %d] [%d]i\n" % (indexed_name, para.min, para.max, default))
            elif para.type == Experiment.ParameterSpec.FLOAT:
                # B [0.00001, 0.1] [0.01]
                default = (para.min + para.max) / 2.0
                # TODO: round to middle
                fh.write("%s [%f, %f] [%f]\n" % (indexed_name, para.min, para.max, default))
            elif para.type == Experiment.ParameterSpec.ENUM:
                # C {a, b, c, 3, 4, 5} [a]
                # TODO: round to middle
                default = para.options[0].strip('"')
                fh.write("%s {%s} [%s]\n" %
                         (indexed_name, ', '.join(i.strip('"') for i in para.options),
                          default))
    fh.close()


def parse_args():
    parser = optparse.OptionParser(usage="\n\tspearmint [options] <experiment/config.pb>")

    parser.add_option("--max-finished-jobs", dest="max_finished_jobs",
                      type="int", default=10000)
    parser.add_option("--grid-seed", dest="grid_seed",
                      help="The seed used to initialize initial grid.",
                      type="int", default=1)
    parser.add_option("-v", "--verbose", action="store_true",
                      help="Print verbose debug output.")

    (options, args) = parser.parse_args()

    if len(args) == 0:
        parser.print_help()
        sys.exit(0)

    return options, args


def main():
    options, args = parse_args()

    experiment_config = args[0]
    expt_dir = os.path.dirname(os.path.realpath(experiment_config))
    print("Using experiment configuration: " + experiment_config)
    print ("experiment dir: " + expt_dir)

    if not os.path.exists(expt_dir):
        print("Cannot find experiment directory '%s'. "
            "Aborting." % (expt_dir))
        sys.exit(-1)

    # Convert search space and create instance file
    spearmint_to_smac(experiment_config)

    # Copy the smac search space and create the instance information
    fh = open(os.path.join(expt_dir, 'train.txt'), "w")
    fh.write(experiment_config + "\n")
    fh.close()

    fh = open(os.path.join(expt_dir, 'test.txt'), "w")
    fh.write(experiment_config + "\n")
    fh.close()

    fh = open(os.path.join(expt_dir, "scenario.txt"), "w")
    fh.close()

    call = os.path.join(os.path.dirname(os.path.realpath(__file__)), "smac/smac")
    call = [call, '--numRun', str(options.grid_seed),
            '--scenario-file', os.path.join(expt_dir, 'scenario.txt'),
            '--runObj', 'QUALITY',
            '--overall_obj', 'MEAN',
            '--cutoff-time', "200000000000",
            '--execDir', expt_dir,
            '-p', experiment_config + ".pcs",
            '--totalNumRunsLimit', str(options.max_finished_jobs),
            '--outputDirectory', expt_dir,
            '--numConcurrentAlgoExecs', "1",
            '--instanceFile', os.path.join(expt_dir, 'train.txt'),
            '--testInstanceFile', os.path.join(expt_dir, 'test.txt'),
            '--deterministic', 'True',
            '--algoExec',  '"python ' + os.path.join(os.path.dirname(os.path.realpath(__file__)),
                "mcwrapsmac.py") + '"']
    print call
    subprocess.call(call)




if __name__ == "__main__":
    main()
