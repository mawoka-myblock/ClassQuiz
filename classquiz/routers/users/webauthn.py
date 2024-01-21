# SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)
#
# SPDX-License-Identifier: MPL-2.0

import urllib.parse

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from webauthn.helpers.cose import COSEAlgorithmIdentifier

from classquiz.auth import get_current_user, verify_password
from classquiz.db.models import User, FidoCredentials
from classquiz.config import redis, settings

import base64

from webauthn import generate_registration_options, verify_registration_response
from webauthn.helpers.structs import (
    AuthenticatorSelectionCriteria,
    UserVerificationRequirement,
    RegistrationCredential,
    PublicKeyCredentialCreationOptions,
    PublicKeyCredentialDescriptor,
)

settings = settings()

router = APIRouter()


class RequirePasswordForAction(BaseModel):
    password: str


@router.post("/add_key_init", response_model=PublicKeyCredentialCreationOptions)
async def request_add_key_data(data: RequirePasswordForAction, user: User = Depends(get_current_user)):
    user = await User.objects.select_related("fidocredentialss").get(id=user.id)
    if not verify_password(data.password, user.password):
        raise HTTPException(status_code=401, detail="Invalid")
    options = generate_registration_options(
        rp_id=urllib.parse.urlparse(settings.root_address).hostname,
        rp_name="ClassQuiz",
        user_id=user.id.hex,
        user_name=user.email,
        exclude_credentials=[
            PublicKeyCredentialDescriptor(id=cred.id, type="public-key", transports=[])
            for cred in user.fidocredentialss
        ],
        authenticator_selection=AuthenticatorSelectionCriteria(user_verification=UserVerificationRequirement.PREFERRED),
        supported_pub_key_algs=[
            COSEAlgorithmIdentifier.ECDSA_SHA_256,
            COSEAlgorithmIdentifier.RSASSA_PKCS1_v1_5_SHA_256,
        ],
        timeout=600,
    )
    await redis.set(f"add_webauthn:{user.id.hex}", base64.b64encode(options.challenge), ex=610)
    return options


@router.post("/add_key")
async def confirm_add_key_data(credential: RegistrationCredential, user: User = Depends(get_current_user)):
    redis_res = await redis.get(f"add_webauthn:{user.id.hex}")
    if redis_res is None:
        raise HTTPException(401)
    current_registration_challenge = base64.b64decode(redis_res)
    credential.id = base64.urlsafe_b64encode(credential.raw_id).decode("utf-8").replace("=", "")
    credential.response.client_data_json = base64.b64decode(credential.response.client_data_json + b"==")
    credential.response.attestation_object = base64.urlsafe_b64decode(credential.response.attestation_object + b"==")
    verification = verify_registration_response(
        credential=credential,
        expected_challenge=current_registration_challenge,
        expected_rp_id=urllib.parse.urlparse(settings.root_address).hostname,
        expected_origin=settings.root_address,
    )
    new_credential = FidoCredentials(
        id=verification.credential_id,
        public_key=verification.credential_public_key,
        sign_count=verification.sign_count,
    )
    user = await User.objects.select_related("fidocredentialss").get(id=user.id)
    await user.fidocredentialss.add(new_credential)


class SecurityKey(BaseModel):
    id: int


@router.get("/list", response_model=list[SecurityKey])
async def list_security_keys(user: User = Depends(get_current_user)):
    user = await User.objects.select_related("fidocredentialss").get(id=user.id)
    return [SecurityKey(id=sec.pk) for sec in user.fidocredentialss]


@router.delete("/key/{key_id}")
async def delete_security_key(data: RequirePasswordForAction, key_id: int, user: User = Depends(get_current_user)):
    if not verify_password(data.password, user.password):
        raise HTTPException(status_code=401, detail="Invalid")
    key = await FidoCredentials.objects.get_or_none(pk=key_id, user=user.id)
    if key is None:
        raise HTTPException(status_code=404, detail="Key not found")
    await key.delete()
