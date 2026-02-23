(* Typed projection proof skeleton for the Fused Fabric project. *)
Require Import Reals.
Require Import Psatz.
Require Import Lra.

Open Scope R_scope.

(* We model a vector as a list of reals; for succinctness we use finite tuple semantics. *)

Definition box_project (lo hi : R) (x : R) : R :=
  if Rle_dec x lo then lo else if Rle_dec hi x then hi else x.

Lemma box_project_in_bounds : forall lo hi x,
  lo <= hi -> lo <= box_project lo hi x <= hi.
Proof.
  intros lo hi x H.
  unfold box_project.
  destruct (Rle_dec x lo).
  - split; lra.
  - destruct (Rle_dec hi x).
    + split; lra.
    + split; lra.
Qed.

(* Distance non-increasing: projection onto convex set is non-expansive. For box (elementwise) we can show |p(x)-y| <= |x-y| when y in [lo,hi]. *)

Lemma box_projection_nonexpansive: forall lo hi x y,
  lo <= hi -> lo <= y <= hi -> Rabs (box_project lo hi x - y) <= Rabs (x - y).
Proof.
  intros lo hi x y Hbox Hy.
  unfold box_project.
  destruct (Rle_dec x lo).
  - (* x <= lo *)
    assert (box_project lo hi x = lo) by (now destruct (Rle_dec hi x)); subst.
    rewrite Rabs_pos_eq, Rabs_pos_eq; try lra.
    lra.
  - destruct (Rle_dec hi x).
    + (* x >= hi *)
      assert (box_project lo hi x = hi) by (now destruct (Rle_dec hi x)); subst.
      rewrite Rabs_pos_eq, Rabs_pos_eq; try lra.
      lra.
    + (* lo < x < hi *)
      assert (box_project lo hi x = x). { unfold box_project; destruct (Rle_dec hi x); lra. }
      rewrite Rabs_Ropp, Rabs_Ropp.
      rewrite Rabs_sym.
      rewrite Rabs_sym.
      lra.
Qed.

(* TODO: extend to vectors (lists) and to projections like simplex projection. *)

(* Admitted lemmas and further formalization can be added later. *)

Qed.
