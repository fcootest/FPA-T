from main import app


def test_all_r20_endpoints_registered():
    paths = {r.path for r in app.routes}
    expected = {
        "/api/fpa-t/r20/schema/{role}",
        "/api/fpa-t/r20/{role}/load",
        "/api/fpa-t/r20/{role}/save-draft",
        "/api/fpa-t/r20/{role}/submit",
        "/api/fpa-t/r20/{role}/validate",
        "/api/fpa-t/r20/batch/{batch_id}",
        "/api/fpa-t/r20/rollback/{batch_id}",
        "/api/fpa-t/r20/refresh-view",
    }
    missing = expected - paths
    assert not missing, f"missing routes: {missing}"
