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

import imp
import os
import sys
import time


from google.protobuf import text_format
from spearmint_pb2 import Experiment, PYTHON
from spearmint_pb2 import *


def read_pb(filename):
    fh = open(filename, 'rb')
    exp = Experiment()
    text_format.Merge(fh.read(), exp)
    fh.close()
    return exp


def main():
    # Now build param dict
    param_list = sys.argv[6:]
    params = dict()

    for idx, i in enumerate(param_list[0::2]):
        params[param_list[idx*2][1:]] = (param_list[idx*2+1].strip("'"))

    exp = read_pb(os.path.basename(sys.argv[1]))
    param_values_as_arrays = dict()
    for para in exp.variable:
        para_array = []
        for i in range(para.size):
            value = params[para.name + "@" + str(i)]
            if para.type == Experiment.ParameterSpec.INT:
                para_array.append(int(float(value)))
            elif para.type == Experiment.ParameterSpec.FLOAT:
                para_array.append(float(value))
            elif para.type == Experiment.ParameterSpec.ENUM:
                para_array.append(value)
            else:
                raise ValueError("Parameter type not recognized.")
        param_values_as_arrays[para.name] = para_array

    print os.getcwd()
    function = imp.load_source(exp.name, exp.name + ".py")
    print function
    fn = function.main
    start_time = time.time()
    res = fn(int(start_time), param_values_as_arrays)
    end_time = time.time()

    print "Result for ParamILS: %s, %d, 0, %f, %d, %s" % ("SAT", end_time - start_time, float(res), -1, " ".join(sys.argv))

if __name__ == "__main__":
    main()
