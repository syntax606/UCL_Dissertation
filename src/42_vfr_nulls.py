import csv, importlib.util, sys, numpy as np, warnings
warnings.filterwarnings("ignore"); sys.path.insert(0,"src")
spec=importlib.util.spec_from_file_location("tp","src/34_timing_probe.py")
TP=importlib.util.module_from_spec(spec); spec.loader.exec_module(TP)
from joblib import Parallel, delayed
CL=("affiliative","neutral","adversarial")
man={r["candidate_id"]:r for r in csv.DictReader(open("data/annotations/annotation_sheet_labeled.csv",newline="")) if r.get("stance","").strip() in CL}
def fp(d):
    st=f"features_frames/{d}/W2_segment"
    X=np.load(f"{st}.X.npy",mmap_mode="r"); L=np.load(f"{st}.lengths.npy")
    ids=[str(c) for c in np.load(f"{st}.ids.npy",allow_pickle=True)]
    rows=[np.concatenate([(F:=np.asarray(X[i,:max(int(L[i]),1)],dtype=np.float64)).mean(0),F.std(0)]) for i in range(len(ids))]
    return np.stack(rows), ids
def pooled(d):
    z=np.load(f"features/{d}/W2_segment.npz",allow_pickle=True)
    return z["X"].reshape(len(z["ids"]),-1), [str(c) for c in z["ids"]]
rng=np.random.default_rng(0)
print(f"{'representation':30}{'dims':>7}{'macroF1':>9}{'null':>8}{'margin':>9}")
for label,fn in [("Sylber",lambda:fp("sylber")),("DyCAST, before quantisation",lambda:fp("dycast_pre")),
                 ("DyCAST, after quantisation",lambda:fp("dycast_post")),
                 ("Mimi, before quantisation",lambda:pooled("mimi_pre"))]:
    X,ids=fn(); keep=[i for i,c in enumerate(ids) if c in man]
    X=np.nan_to_num(X[keep].astype(np.float32))
    y=np.array([man[ids[i]]["stance"] for i in keep]); g=np.array([man[ids[i]]["episode_id"] for i in keep])
    R=TP.repeated_f1(X,y,g,25); fold=TP._partition(g,0)
    null=float(np.mean(Parallel(n_jobs=-1)(delayed(TP._score_partition)(X,rng.permutation(y),fold) for _ in range(50))))
    print(f"{label:30}{X.shape[1]:>7}{R.mean():>9.3f}{null:>8.3f}{R.mean()-null:>+9.3f}")
