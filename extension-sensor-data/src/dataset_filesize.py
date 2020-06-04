import os
import glob
import subprocess
import numpy as np

__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))

def get_file_sizes(path):
    output = subprocess.check_output(["du","-ah", path]).decode("utf-8")
    file_sizes = {}
    for line in output.split("\n")[:-2]:    
        file_size = line.split()[0]
        filename = os.path.basename(line.split()[1]).split(".")[0]
        file_sizes[filename] = file_size
    return file_sizes

def total_dataset_comparison(path_sql, path_sql_parts, translate):
    
    def get_directory_size(path):
        return subprocess.check_output(["du","-sh", path]).split()[0].decode("utf-8")
        
    def add_file_sizes(values, translate):
        float_values = []
        for value in values:
            size = value[-1]
            float_value = float(value[:-1])
            float_values.append(float_value / translate[size])
        return round(sum(float_values), 0)
        
    sql_size = get_directory_size(path_sql)
    sql_parts_size = get_directory_size(path_sql_parts)
    size_mysqldumps = add_file_sizes([sql_size, sql_parts_size], translate)
    
    dataset_path = os.path.join(__location__, "data-collection")
    dataset = [os.path.basename(file).split(".")[0] for file in glob.glob(os.path.join(dataset_path, "*.parquet.snappy")) if os.path.basename(file).split(".")[0][-1].isalpha()]
    file_sizes = [file_size for filename, file_size in get_file_sizes(dataset_path).items() if filename in dataset]
    size_dataset_parquet = add_file_sizes(file_sizes, translate)
    ratio_parquet_mysqldump = size_dataset_parquet/size_mysqldumps
    
    print("Total comparison")
    print("MySQL dumps: {} G".format(size_mysqldumps))
    print("Dataset parquet: {} G".format(size_dataset_parquet))
    print("MySQL dumps and parquet, ratio: {:.1%} / save space: {:.1%}".format(ratio_parquet_mysqldump, 1-ratio_parquet_mysqldump))

def per_file_comparison(path_sql_parts, path_snappy_parts, translate):
    file_sizes_sql_parts = get_file_sizes(path_sql_parts)
    file_sizes_snappy_parts = get_file_sizes(path_snappy_parts)
    print("\nPer file comparison")
    ratios_file_size = []
    for filename_sql, file_size_sql in file_sizes_sql_parts.items():
        file_size_snappy = file_sizes_snappy_parts[filename_sql]
        ratio_file_size = (float(file_size_snappy[:-1])/translate[file_size_snappy[-1]]) / (float(file_size_sql[:-1])/translate[file_size_sql[-1]])
        ratios_file_size.append(ratio_file_size)
        print("{} ratio: {:.1%}, save space: {:.1%}".format(filename_sql, ratio_file_size, 1-ratio_file_size))
    print("Average ratio SQL dump vs. snappy: {:.1%}, save space: {:.1%}".format(np.mean(ratios_file_size), 1-np.mean(ratios_file_size)))

def main():
    translate = {"M": 1e3, "K": 1e6, "G": 1}
    basepath = os.path.join(__location__, "dataset-generation")
    path_snappy_parts = os.path.join(basepath, "snappy-parts")
    path_sql_parts = os.path.join(basepath, "sql-parts")
    path_sql = os.path.join(basepath, "sql")
    total_dataset_comparison(path_sql, path_sql_parts, translate)
    per_file_comparison(path_sql_parts, path_snappy_parts, translate)
    
if __name__== "__main__":
    main()
