@test "invoking foo with a nonexistent file prints an error" {
  cd $BATS_TMPDIR
  run $BATS_TEST_DIRNAME\script_setup.sh

  [ "$status" -eq 1 ]
  [ "$output" = "Setup instructions failed!'" ]
}
$BATS_TMPDIR