import subprocess

def check_gpu():
    try:
        output = subprocess.check_output(['lspci', '-nnk'], universal_newlines=True)
        gpu_info = []
        for line in output.split('\n'):
            if 'VGA' in line:
                gpu_info.append(line.strip())
        if gpu_info:
            return gpu_info
        else:
            return "No GPU found."
    except subprocess.CalledProcessError:
        return "Unable to determine GPU information."

if __name__ == "__main__":
    gpu_info = check_gpu()
    print("GPU Information:", gpu_info)
