from __future__ import division
import numpy
import rpy2.robjects.numpy2ri
rpy2.robjects.numpy2ri.activate()
from rpy2.robjects import r
from rpy2.robjects.packages import importr

'''
To use external R packages in Conda you will install these packages in Conda.
If you install them from R you can't use them. To install (e.g. for dtw library) it do next like:
https://stackoverflow.com/questions/32983365/rpy2-cannot-find-installed-external-r-packages

https://cran.r-project.org/web/packages/dtw/dtw.pdf

conda install rpy2
install.packages(file.choose(), repos=NULL)
remove.packages("...")

packageurl <- "https://cran.r-project.org/src/contrib/Archive/proxy/proxy_0.4-20.tar.gz"
install.packages(packageurl, repos=NULL, type="source")

library(dtw)
query <- c(0, 0, 1, 2, 1, 0, 1, 0, 0)
template <- c(0, 1, 2, 0, 0, 0, 0, 0, 0)
alignment <- dtw(query, template, keep=TRUE)
alignment$distance
alignment$normalizedDistance
'''

class Dtw:
      
    def __init__(self):
        # Set up R namespaces
        try:
            r('memory.limit(size=16000)')
            self.R = rpy2.robjects.r
            self.DTW = importr('dtw')
        except Exception as err:
            print(err)
      
    # dissimilarity matrix for each row (default), now column (transpose)
    def dissimilarity(self, data):
        return self.R.dist(data.transpose(), data.transpose(), method="DTW")[1]
      
    def apply_warp_query(self, alignment, query):
        warp_query = self.R.warp(alignment, index=False)
        warp_query_idx = numpy.array(warp_query, dtype=int) - 1
        return query[warp_query_idx]
      
    def apply_warp(self, alignment, query, template):
        warp_query = self.R.warp(alignment, index=False)
        warp_query_idx = numpy.array(warp_query, dtype=int) - 1
        warp_template = self.R.warp(alignment, index=True)
        warp_template_idx = numpy.array(warp_template, dtype=int) - 1
        return query[warp_query_idx], template[warp_template_idx]
       
    def calculate_alignment(self, query, template):
        return self.R.dtw(query, template, keep=True)
      
    def get_normalized_distance(self, alignment):
        return alignment.rx('normalizedDistance')[0][0]
       
    def get_distance(self, alignment):
        return alignment.rx('distance')[0][0]

def install_dtw_package():
    utils = importr("utils")
    #utils.install_packages("dtw")
    utils.install_packages("dtw", repos="http://cran.us.r-project.org")
    
def platform_info():
    base = importr('base')
    print(base._libPaths())
    print(r('memory.limit()'))

def test_dtw():
    dtw = Dtw()
    template = numpy.array([0, 0, 1, 2, 1, 0, 1, 0, 0], dtype=numpy.double)
    query = numpy.array([0.0, 1, 2, 0, 0, 0, 0, 0, 0])
    alignment = dtw.calculate_alignment(query, template)
    print("distance:", dtw.get_distance(alignment))
    print("normalized distance:", dtw.get_normalized_distance(alignment))
    
def main():
    #install_dtw_package()
    #platform_info()
    test_dtw()
    
if __name__ == "__main__":
    main()
    