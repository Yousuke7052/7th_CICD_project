version: 1
stages:
  - name: Build
    steps:
      - name: Checkout
        uses: checkout@v1
      - name: Setup Python
        uses: setup-python@v1
        with:
          python-version: '3.x'
      - name: Run Script
        run: |
          # 输出环境变量以验证它们是否被正确设置
          echo "Checking environment variables..."
          env | grep OSS
          # 运行Python脚本
          python /path/to/your/script.py