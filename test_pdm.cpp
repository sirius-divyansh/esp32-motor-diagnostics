// test_pdm.cpp - PC harness for pdm_infer.h (NOT part of the ESP32 firmware).
//
// build:  g++ -O2 -std=c++11 -Wall -Wextra -fno-exceptions -fno-rtti test_pdm.cpp -o test_pdm -lm
// run:    ./test_pdm test_windows.bin test_py_features.bin cpp_out.csv
//
// test_windows.bin     float32 [count x PDM_N]     raw current windows [A]
// test_py_features.bin float32 [count x PDM_NFEAT] features computed by Python
//
// For every window it reports
//   pred_full  : C++ features (from raw samples) -> C++ forest   (what the ESP32 would do)
//   pred_model : PYTHON features                 -> C++ forest   (isolates the model export)
// plus the C++ feature vector, so Python can check the feature extraction itself.
#include <cstdio>
#include <cstdlib>
#include <vector>
#include "pdm_infer.h"

int main(int argc, char **argv) {
    if (argc < 4) { std::fprintf(stderr, "usage: %s windows.bin py_features.bin out.csv\n", argv[0]); return 2; }
    std::FILE *fw = std::fopen(argv[1], "rb");
    std::FILE *ff = std::fopen(argv[2], "rb");
    std::FILE *fo = std::fopen(argv[3], "w");
    if (!fw || !ff || !fo) { std::fprintf(stderr, "cannot open files\n"); return 2; }

    pdm_init();
    std::vector<float> win(PDM_N), pyf(PDM_NFEAT);
    float cf[PDM_NFEAT];
    int idx = 0;
    std::fprintf(fo, "idx,pred_full,pred_model");
    for (int i = 0; i < PDM_NFEAT; i++) std::fprintf(fo, ",f%d", i);
    std::fprintf(fo, "\n");

    while (std::fread(win.data(), sizeof(float), PDM_N, fw) == (size_t)PDM_N &&
           std::fread(pyf.data(), sizeof(float), PDM_NFEAT, ff) == (size_t)PDM_NFEAT) {
        for (int n = 0; n < PDM_N; n++) pdm_re[n] = win[n];
        const int pred_full = pdm_classify(cf);
        const int pred_model = pdm_predict(pyf.data());
        std::fprintf(fo, "%d,%d,%d", idx, pred_full, pred_model);
        for (int i = 0; i < PDM_NFEAT; i++) std::fprintf(fo, ",%.9g", (double)cf[i]);
        std::fprintf(fo, "\n");
        idx++;
    }
    std::fclose(fw); std::fclose(ff); std::fclose(fo);
    std::printf("processed %d windows\n", idx);
    return 0;
}
