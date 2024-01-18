"""This integration test is designed to ensure that the chemprop model can _overfit_ the training
data. A small enough dataset should be memorizable by even a moderately sized model, so this test
should generally pass."""

import warnings
from pathlib import Path

import pandas as pd
import pytest
import torch
from lightning import pytorch as pl
from torch.utils.data import DataLoader

from chemprop import featurizers, nn
from chemprop.data import (MoleculeDatapoint, MoleculeDataset,
                           MulticomponentDataset, collate_multicomponent)
from chemprop.models import multi

N_COMPONENTS = 2
pytestmark = pytest.mark.parametrize(
    "mcmpnn", [(nn.BondMessagePassing(), N_COMPONENTS), (nn.AtomMessagePassing(), N_COMPONENTS)], indirect=True
)

@pytest.fixture
def datas(mol_mol_regression_data):
    smis1, smis2, Y = mol_mol_regression_data

    return [[MoleculeDatapoint.from_smi(smi, y) for smi, y in zip(smis1, Y)], [MoleculeDatapoint.from_smi(smi) for smi in smis2]]


@pytest.fixture
def dataloader_scaler(datas):
    dsets = [MoleculeDataset(data) for data in datas]
    mcdset = MulticomponentDataset(dsets)
    scaler = mcdset.normalize_targets()

    return DataLoader(mcdset, 32, collate_fn=collate_multicomponent), scaler


def test_quick(mcmpnn, dataloader_scaler):
    dataloader, _ = dataloader_scaler
    trainer = pl.Trainer(
        logger=False,
        enable_checkpointing=False,
        enable_progress_bar=False,
        enable_model_summary=False,
        accelerator="cpu",
        devices=1,
        fast_dev_run=True,
    )
    trainer.fit(mcmpnn, dataloader)


def test_overfit(mcmpnn, dataloader_scaler):
    dataloader, scaler = dataloader_scaler
    mcmpnn.loc = scaler.mean_
    mcmpnn.scale = scaler.scale_
    trainer = pl.Trainer(
        logger=False,
        enable_checkpointing=False,
        enable_progress_bar=True,
        enable_model_summary=False,
        accelerator="cpu",
        devices=1,
        max_epochs=100,
        overfit_batches=1.00
    )
    trainer.fit(mcmpnn, dataloader)

    errors = []
    for batch in dataloader:
        bmg, _, _, targets, *_ = batch
        preds = mcmpnn(bmg)
        errors.append(preds - targets)

    errors = torch.cat(errors)
    mse = errors.square().mean().item()

    assert mse <= 0.05
