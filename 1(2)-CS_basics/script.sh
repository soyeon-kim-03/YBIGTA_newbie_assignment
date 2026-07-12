
# anaconda(또는 miniconda)가 존재하지 않을 경우 설치해주세요!
## TODO
export PATH="$HOME/miniconda3/bin:$PATH"

if ! command -v conda &> /dev/null; then
    echo "[INFO] conda가 설치되어 있지 않아 Miniconda를 설치합니다..."
    wget -q https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O ~/miniconda.sh
    bash ~/miniconda.sh -b -p "$HOME/miniconda3"
    rm ~/miniconda.sh
fi

source "$HOME/miniconda3/etc/profile.d/conda.sh"

# Conda 환셩 생성 및 활성화
## TODO
conda tos accept --override-channels --channel https://repo.anaconda.com/pkgs/main
conda tos accept --override-channels --channel https://repo.anaconda.com/pkgs/r

if ! conda env list | grep -q "myenv"; then
    echo "[INFO] myenv 가상환경을 생성합니다..."
    conda create -y -n myenv python=3.11
fi

conda activate myenv

## 건드리지 마세요! ##
python_env=$(python -c "import sys; print(sys.prefix)")
if [[ "$python_env" == *"/envs/myenv"* ]]; then
    echo "[INFO] 가상환경 활성화: 성공"
else
    echo "[INFO] 가상환경 활성화: 실패"
    exit 1 
fi

# 필요한 패키지 설치
## TODO
pip install --quiet mypy

# Submission 폴더 파일 실행
cd submission || { echo "[INFO] submission 디렉토리로 이동 실패"; exit 1; }

for file in *.py; do
    ## TODO
    problem_num=$(echo "$file" | sed -E 's/^[0-9]+_([0-9]+)\.py$/\1/')
    input_file="../input/${problem_num}_input"
    output_file="../output/${problem_num}_output"

    if [ -f "$input_file" ]; then
        python "$file" < "$input_file" > "$output_file"
        echo "[INFO] $file 실행 완료 -> $output_file"
    else
        echo "[INFO] $file: 입력 파일($input_file)을 찾을 수 없습니다."
    fi

done

# mypy 테스트 실행 및 mypy_log.txt 저장
## TODO
echo "mypy 테스트 결과" > ../mypy_log.txt
for file in *.py; do
    echo "===== $file =====" >> ../mypy_log.txt
    mypy "$file" >> ../mypy_log.txt 2>&1
done

# conda.yml 파일 생성
## TODO
conda env export > ../conda.yml

# 가상환경 비활성화
## TODO
conda deactivate

echo "[INFO] 모든 작업이 완료되었습니다."